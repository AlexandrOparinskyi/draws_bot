import logging
import random
import asyncio
import time
from typing import List, Optional
from collections import Counter

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from database import User, Channel, Raffle
from reg_bot.utils import get_referrals_count
from . import make_place_to_player
from .database import get_raffle_by_id, edit_raffle_to_complete

logger = logging.getLogger(__name__)


async def completed_raffle_bulk(
        raffle_id: int,
        check_bot: Bot,
        bot: Bot,
        batch_size: int = 100,  # Увеличил для 4к участников
        max_concurrent: int = 30,  # Увеличил для параллельности
        use_cache: bool = True  # Кэширование результатов
) -> None:
    """
    Оптимизированная версия для большого количества участников.

    Args:
        batch_size: Размер батча для обработки (оптимально 100-200)
        max_concurrent: Максимальное количество одновременных запросов
        use_cache: Использовать кэш для проверок подписок
    """
    start_time = time.time()

    # 1. Получаем данные розыгрыша
    raffle = await get_raffle_by_id(raffle_id)
    if not raffle:
        logger.error(f"Raffle {raffle_id} not found")
        return

    total_players = len(raffle.players)
    logger.info(
        f"Starting bulk completion for {total_players} participants, "
        f"{len(raffle.channels)} channels"
    )

    # 2. Кэш для проверок подписок (чтобы не проверять повторно)
    subscription_cache = {}

    # 3. Батчевая проверка подписок
    eligible_players = await _bulk_check_subscriptions(
        players=raffle.players,
        channels=raffle.channels,
        check_bot=check_bot,
        batch_size=batch_size,
        max_concurrent=max_concurrent,
        use_cache=use_cache,
        cache=subscription_cache
    )

    eligible_count = len(eligible_players)
    logger.info(f"Eligible players: {eligible_count}/{total_players}")

    if not eligible_players:
        logger.warning("No eligible players found")
        await _handle_no_participants(raffle, bot)
        return

    # 4. Формируем пул участников с учетом рефералов
    participants_pool = await _build_participants_pool_bulk(
        players=eligible_players,
        raffle_id=raffle.id,
        has_ref_system=raffle.ref_system
    )

    pool_size = len(participants_pool)
    logger.debug(f"Participants pool size: {pool_size}")

    # 5. Выбираем победителей
    winners = _select_winners_fast(
        participants_pool=participants_pool,
        winners_count=raffle.winners_count
    )

    logger.info(f"Selected {len(winners)} winners")

    # 6. Обновляем статус розыгрыша
    await edit_raffle_to_complete(raffle_id)

    # 7. Рассылка уведомлений
    notification_result = await _bulk_notify_winners(
        winners=winners,
        bot=bot,
        raffle=raffle,
        batch_size=50  # Меньше для рассылки
    )

    # 8. Уведомляем организатора
    await _notify_owner_bulk_stats(
        owner_id=raffle.user_id,
        bot=check_bot,
        raffle=raffle,
        total_players=total_players,
        eligible_count=eligible_count,
        winners=winners,
        notification_stats=notification_result
    )

    elapsed = time.time() - start_time
    logger.info(
        f"Bulk raffle {raffle_id} completed in {elapsed:.2f}s "
        f"({elapsed / total_players * 1000:.1f}ms per player)"
    )


async def _bulk_check_subscriptions(
        players: List[User],
        channels: List[Channel],
        check_bot: Bot,
        batch_size: int = 100,
        max_concurrent: int = 30,
        use_cache: bool = True,
        cache: Optional[dict] = None
) -> List[User]:
    """
    Массовая проверка подписок с оптимизациями.
    """
    if not channels:
        return players

    if cache is None:
        cache = {}

    eligible_players = []
    semaphore = asyncio.Semaphore(max_concurrent)

    # Счетчики для статистики
    cached_count = 0
    checked_count = 0

    # Разбиваем на батчи
    total_batches = (len(players) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = start_idx + batch_size
        batch = players[start_idx:end_idx]

        logger.debug(f"Processing batch {batch_num + 1}/{total_batches}")

        # Проверяем батч параллельно
        batch_tasks = []
        for player in batch:
            cache_key = f"{player.id}:{','.join(str(c.chat_id) for c in channels)}"

            # Проверяем кэш
            if use_cache and cache_key in cache:
                cached_count += 1
                is_eligible = cache[cache_key]
                if is_eligible:
                    eligible_players.append(player)
                continue

            # Создаем задачу для проверки
            task = _check_player_subscriptions_with_cache(
                check_bot=check_bot,
                player=player,
                channels=channels,
                semaphore=semaphore,
                cache_key=cache_key if use_cache else None,
                cache=cache if use_cache else None
            )
            batch_tasks.append(task)
            checked_count += 1

        # Обрабатываем результаты
        if batch_tasks:
            batch_results = await asyncio.gather(*batch_tasks,
                                                 return_exceptions=True)

            for player, result in zip(batch[-len(batch_tasks):], batch_results):
                if isinstance(result, tuple) and result[
                    0]:  # (is_eligible, cache_key)
                    eligible_players.append(player)

        # Задержка между батчами чтобы не перегружать API
        if batch_num % 10 == 0 and batch_num > 0:
            await asyncio.sleep(0.5)

    logger.debug(f"Cache hits: {cached_count}, checks: {checked_count}")
    return eligible_players


async def _check_player_subscriptions_with_cache(
        check_bot: Bot,
        player: User,
        channels: List[Channel],
        semaphore: asyncio.Semaphore,
        cache_key: Optional[str] = None,
        cache: Optional[dict] = None
) -> tuple[bool, Optional[str]]:
    """
    Проверка подписок с кэшированием результата.
    """
    async with semaphore:
        try:
            is_eligible = await _check_all_channels_parallel(
                check_bot=check_bot,
                user_id=player.id,
                channels=channels
            )

            # Сохраняем в кэш
            if cache_key and cache is not None:
                cache[cache_key] = is_eligible

            return (is_eligible, cache_key)

        except Exception as e:
            logger.warning(f"Error checking player {player.id}: {e}")
            return (False, cache_key)


async def _check_all_channels_parallel(
        check_bot: Bot,
        user_id: int,
        channels: List[Channel]
) -> bool:
    """
    Параллельная проверка всех каналов для одного пользователя.
    """
    if not channels:
        return True

    # Группируем каналы по приоритету (если есть)
    channel_ids = [channel.chat_id for channel in channels]

    # Создаем задачи для всех каналов
    tasks = []
    for channel_id in channel_ids:
        task = asyncio.create_task(
            _check_single_channel_fast(check_bot, channel_id, user_id)
        )
        tasks.append(task)

    # Ждем все проверки с таймаутом
    try:
        done, pending = await asyncio.wait(
            tasks,
            timeout=3.0,  # Уменьшил таймаут
            return_when=asyncio.ALL_COMPLETED
        )

        # Отменяем оставшиеся задачи
        for task in pending:
            task.cancel()

        # Проверяем результаты
        for task in done:
            try:
                result = task.result()
                if not result:  # Если хотя бы один канал не пройден
                    return False
            except Exception:
                return False

    except asyncio.TimeoutError:
        logger.debug(f"Timeout checking user {user_id}")
        return False

    return True


async def _check_single_channel_fast(
        bot: Bot,
        channel_id: int,
        user_id: int
) -> bool:
    """
    Быстрая проверка одного канала.
    """
    try:
        member = await asyncio.wait_for(
            bot.get_chat_member(channel_id, user_id),
            timeout=1.5  # Уменьшил таймаут
        )
        return member.status not in ["left", "kicked", "restricted"]

    except TelegramBadRequest as e:
        if "PARTICIPANT_ID_INVALID" in str(e):
            return False
        logger.debug(
            f"Telegram error for user {user_id}, channel {channel_id}: {e}")
        return False

    except asyncio.TimeoutError:
        logger.debug(f"Timeout for user {user_id}, channel {channel_id}")
        return False

    except Exception as e:
        logger.debug(
            f"Error checking user {user_id}, channel {channel_id}: {e}")
        return False


async def _build_participants_pool_bulk(
        players: List[User],
        raffle_id: int,
        has_ref_system: bool
) -> List[User]:
    """
    Массовое формирование пула участников.
    """
    if not has_ref_system:
        return players

    participants_pool = []

    # Используем Counter для оптимизации
    if len(players) > 1000:
        # Для больших объемов разбиваем на батчи
        batch_size = 200
        total_batches = (len(players) + batch_size - 1) // batch_size

        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = start_idx + batch_size
            batch = players[start_idx:end_idx]

            # Получаем количество рефералов для батча
            batch_tasks = [
                get_referrals_count(player.id, raffle_id)
                for player in batch
            ]

            batch_ref_counts = await asyncio.gather(*batch_tasks)

            # Формируем пул
            for player, ref_count in zip(batch, batch_ref_counts):
                weight = ref_count + 1
                participants_pool.extend([player] * weight)
    else:
        # Для небольших объемов обрабатываем сразу
        ref_counts = await asyncio.gather(*[
            get_referrals_count(player.id, raffle_id)
            for player in players
        ])

        for player, ref_count in zip(players, ref_counts):
            weight = ref_count + 1
            participants_pool.extend([player] * weight)

    return participants_pool


def _select_winners_fast(
        participants_pool: List[User],
        winners_count: int
) -> List[User]:
    """
    Быстрый выбор победителей.
    """
    if not participants_pool:
        return []

    # Уникальные участники с весами
    weighted_counter = Counter(participants_pool)
    unique_participants = list(weighted_counter.keys())
    weights = list(weighted_counter.values())

    if winners_count >= len(unique_participants):
        return unique_participants

    # Выбор с учетом весов (шансы пропорциональны количеству рефералов)
    try:
        winners = random.choices(
            population=unique_participants,
            weights=weights,
            k=winners_count
        )
        # Убираем дубликаты
        winners = list(dict.fromkeys(winners))

        # Если из-за уникальности победителей стало меньше, добираем
        while len(winners) < winners_count and len(winners) < len(
                unique_participants):
            remaining = [p for p in unique_participants if p not in winners]
            additional = random.sample(remaining,
                                       min(winners_count - len(winners),
                                           len(remaining)))
            winners.extend(additional)

        return winners

    except Exception as e:
        logger.error(f"Error in weighted selection: {e}")
        # Fallback: обычный выбор без весов
        return random.sample(unique_participants,
                             min(winners_count, len(unique_participants)))


async def _bulk_notify_winners(
        winners: List[User],
        bot: Bot,
        raffle: Raffle,
        batch_size: int = 50
) -> dict:
    """
    Массовая рассылка уведомлений победителям.
    Возвращает статистику.
    """
    if not winners:
        return {"success": 0, "failed": 0, "blocked": 0}

    success = 0
    failed = 0
    blocked = 0

    total_batches = (len(winners) + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = start_idx + batch_size
        batch = winners[start_idx:end_idx]

        logger.debug(f"Notifying batch {batch_num + 1}/{total_batches}")

        # Отправляем батч параллельно
        batch_tasks = []
        for place_offset, winner in enumerate(batch, 1):
            place = start_idx + place_offset
            task = _notify_single_winner(bot, winner, raffle, place)
            batch_tasks.append(task)

        # Обрабатываем результаты батча
        batch_results = await asyncio.gather(*batch_tasks,
                                             return_exceptions=True)

        for result in batch_results:
            if result == "success":
                success += 1
            elif result == "blocked":
                blocked += 1
                failed += 1
            else:
                failed += 1

        # Задержка между батчами рассылки
        if batch_num % 5 == 0 and batch_num > 0:
            await asyncio.sleep(0.3)

    logger.info(
        f"Winner notifications: {success} success, {failed} failed "
        f"({blocked} blocked)"
    )

    return {"success": success, "failed": failed, "blocked": blocked}


async def _notify_single_winner(
        bot: Bot,
        winner: User,
        raffle: Raffle,
        place: int
) -> str:
    """
    Уведомление одного победителя.
    Возвращает: "success", "blocked", "error"
    """
    try:
        # Сохраняем в БД
        await make_place_to_player(place, winner.id, raffle.id)

        # Отправляем сообщение
        await bot.send_message(
            chat_id=winner.id,
            text=(
                f"🎉 <b>Поздравляем!</b>\n\n"
                f"Вы заняли <b>{place}</b> место "
                f"в розыгрыше <b>«{raffle.title}»</b>\n\n"
                f"С вами скоро свяжется организатор для получения приза."
            ),
            parse_mode=ParseMode.HTML
        )
        return "success"

    except TelegramBadRequest as e:
        if "chat not found" in str(e) or "USER_IS_BLOCKED" in str(e):
            logger.debug(f"Winner {winner.id} blocked bot")
            return "blocked"
        logger.warning(f"Telegram error for winner {winner.id}: {e}")
        return "error"

    except Exception as e:
        logger.warning(f"Error notifying winner {winner.id}: {e}")
        return "error"


async def _notify_owner_bulk_stats(
        owner_id: int,
        bot: Bot,
        raffle: Raffle,
        total_players: int,
        eligible_count: int,
        winners: List[User],
        notification_stats: Optional[dict] = None
) -> None:
    """
    Отправка подробной статистики организатору.
    """
    try:
        # Форматируем список победителей
        winners_text = ""
        if winners:
            winners_text = "\n🏆 <b>Победители:</b>\n"
            for place, winner in enumerate(winners, 1):
                username = _format_username(winner)
                winners_text += f"{place}. {username}\n"
            winners_text += "\n📨 <b>Свяжитесь с победителями!</b>"

        # Добавляем статистику рассылки
        stats_text = ""
        if notification_stats:
            stats_text = (
                f"\n📊 <b>Статистика рассылки:</b>\n"
                f"• Успешно: {notification_stats.get('success', 0)}\n"
                f"• Не отправлено: {notification_stats.get('failed', 0)}\n"
                f"• Заблокировали бота: {notification_stats.get('blocked', 0)}"
            )

        text = (
            f"✅ <b>Розыгрыш «{raffle.title}» завершен</b>\n\n"
            f"📈 <b>Общая статистика:</b>\n"
            f"• Всего участников: {total_players}\n"
            f"• Прошли проверку: {eligible_count}\n"
            f"• Победителей выбрано: {len(winners)}\n"
            f"{stats_text}"
            f"{winners_text}"
        )

        await bot.send_message(
            chat_id=owner_id,
            text=text,
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"Failed to notify owner {owner_id}: {e}")


async def _handle_no_participants(raffle: Raffle, bot: Bot) -> None:
    """
    Обработка случая когда нет подходящих участников.
    """
    try:
        await edit_raffle_to_complete(raffle.id)

        await bot.send_message(
            chat_id=raffle.user_id,
            text=(
                f"❌ <b>Розыгрыш «{raffle.title}» завершен</b>\n\n"
                f"Не нашлось участников, подписанных на все необходимые каналы.\n\n"
                f"<i>Рекомендация: упростите условия или выберите другие каналы.</i>"
            ),
            parse_mode=ParseMode.HTML
        )

    except Exception as e:
        logger.error(f"Error handling no participants: {e}")


def _format_username(user: User) -> str:
    """
    Форматирует имя пользователя для отображения.
    """
    if user.username:
        return f"@{user.username}"

    parts = []
    if user.first_name:
        parts.append(user.first_name)
    if user.last_name:
        parts.append(user.last_name)

    return " ".join(parts) if parts else f"ID: {user.id}"

completed_raffle = completed_raffle_bulk