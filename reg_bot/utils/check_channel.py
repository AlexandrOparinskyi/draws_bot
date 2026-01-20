import asyncio
import logging
from typing import Optional, Dict, List

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)


async def check_single_channel_safe(bot: Bot, channel: int, user_id: int) -> bool:
    """Безопасная проверка подписки на один канал с таймаутом"""
    try:
        # Добавляем таймаут 3 секунды
        member = await asyncio.wait_for(
            bot.get_chat_member(channel, user_id),
            timeout=3.0
        )
        return member.status != "left"
    except TelegramBadRequest as e:
        # Если пользователя нет в канале или канал не найден
        return False
    except asyncio.TimeoutError:
        logger.warning(f"Timeout checking channel {channel}")
        return False
    except Exception as e:
        logger.error(f"Error checking channel {channel}: {e}")
        return False


async def check_all_subscriptions_parallel(
        check_bot: Bot,
        user_id: int,
        channels,
        main_channel_id: Optional[str] = None
) -> Dict:
    """
    Параллельная проверка всех подписок для команды /start.

    Returns:
        {
            "all_subscribed": bool,
            "main_channel_subscribed": bool,
            "unsubscribed_channels": List[int]
        }
    """
    # Собираем ID всех каналов для проверки
    channel_checks = []

    # Основной канал (если указан)
    if main_channel_id:
        channel_checks.append(("main", main_channel_id))

    # Дополнительные каналы
    for channel in channels:
        channel_checks.append(("additional", channel.chat_id))

    # Если нет каналов для проверки
    if not channel_checks:
        return {
            "all_subscribed": True,
            "main_channel_subscribed": True,
            "unsubscribed_channels": []
        }

    # Создаем задачи для параллельной проверки
    tasks = []
    for channel_type, channel_id in channel_checks:
        task = asyncio.create_task(
            check_single_channel_safe(check_bot, channel_id, user_id)
        )
        tasks.append((channel_type, channel_id, task))

    # Запускаем все проверки параллельно
    try:
        results = await asyncio.gather(
            *[task for _, _, task in tasks],
            return_exceptions=True
        )
    except Exception as e:
        logger.error(f"Error in parallel checks: {e}")
        # В случае ошибки считаем, что не подписан
        return {
            "all_subscribed": False,
            "main_channel_subscribed": False,
            "unsubscribed_channels": [c.chat_id for c in channels]
        }

    # Анализируем результаты
    main_subscribed = True
    unsubscribed = []

    for (channel_type, channel_id), result in zip(
            [(t, c) for t, c, _ in tasks], results
    ):
        if isinstance(result, Exception) or not result:
            if channel_type == "main":
                main_subscribed = False
            else:
                unsubscribed.append(channel_id)

    return {
        "all_subscribed": main_subscribed and not unsubscribed,
        "main_channel_subscribed": main_subscribed,
        "unsubscribed_channels": unsubscribed
    }


async def check_subscriptions_quick(
        check_bot: Bot,
        user_id: int,
        channel_ids: List[int],
        timeout_per_channel: float = 1.5
) -> List[bool]:
    """
    Быстрая проверка списка каналов.
    Возвращает список результатов для каждого канала.
    """
    if not channel_ids:
        return []

    # Создаем задачи
    tasks = []
    for channel_id in channel_ids:
        task = asyncio.create_task(
            check_single_channel_safe(
                check_bot, channel_id, user_id, timeout_per_channel
            )
        )
        tasks.append(task)

    # Запускаем параллельно
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        logger.error(f"Error in quick checks: {e}")
        return [False] * len(channel_ids)

    # Преобразуем исключения в False
    return [
        False if isinstance(r, Exception) else r
        for r in results
    ]
