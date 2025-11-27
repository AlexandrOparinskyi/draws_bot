import logging
import random

from aiogram import Bot
from aiogram.enums import ParseMode

from bot.utils import get_raffle_by_id, edit_raffle_to_complete
from database import User, Channel, Raffle
from reg_bot.utils import get_referrals_count

logger = logging.getLogger(__name__)


async def completed_raffle(raffle_id: int,
                           check_bot: Bot,
                           bot: Bot) -> None:
    raffle = await get_raffle_by_id(raffle_id)
    channels = raffle.channels

    if not raffle:
        logger.error(f"On the finish raffle with id {raffle_id} not found")
        return

    participants_pool = []
    for player in raffle.players:
        if not await _check_subscribes(check_bot, player, channels):
            continue

        if raffle.ref_system:
            referrals_count = await get_referrals_count(player.id)
            participants_pool.extend([player] * (referrals_count + 1))
        else:
            participants_pool.append(player)

    winners = []
    while len(winners) < raffle.winners_count and participants_pool:
        winner = random.choice(participants_pool)
        if winner not in winners:
            winners.append(winner)

        participants_pool = [p for p in participants_pool if p != winner]

    # await edit_raffle_to_complete(raffle_id)
    await _winners_mailing(winners, bot, raffle.title)
    await _owner_mailing(raffle.user_id, check_bot, raffle.title, winners)


async def _check_subscribes(check_bot: Bot,
                            user: User,
                            channels: list[Channel]) -> bool:
    for channel in channels:
        member = await check_bot.get_chat_member(channel.chat_id,
                                                 user.id)
        if member.status == "left":
            return False

    return True


async def _winners_mailing(winners: list[User], bot: Bot, title: str) -> None:
    for place, winner in enumerate(winners, 1):
        try:
            await bot.send_message(
                chat_id=winner.id,
                text=f"Поздравляем 🔥\n\n"
                     f"Вы заняли {place} место в розыгрыше <b>{title}</b>\n\n"
                     f"Скоро с вами свяжется организатор",
                parse_mode=ParseMode.HTML
            )
        except Exception as err:
            logger.error(f"Error send winners text to user {winner.id} {err}")
            continue


async def _owner_mailing(owner_id: int,
                         bot: Bot,
                         title: str,
                         winners: list[User]) -> None:
    text = (f"Розыгрыш <b>{title}</b> завершен 🌟\n\n"
            f"Победители:\n")

    for place, winner in enumerate(winners, 1):
        username = (f"@{winner.username}" if winner.username
                    else f"{winner.first_name} {winner.last_name}")
        text += f"• <b>{place} место</b> - {username}\n"

    text += f"\n❗ Не забудьте написать победителям"

    try:
        await bot.send_message(chat_id=owner_id,
                               text=text)
    except Exception as err:
        logger.error(f"Error send owner text to finish raffle: {err}")
