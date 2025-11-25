import logging

from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import Config, load_config
from database import Raffle

logger = logging.getLogger(__name__)


async def send_mail_to_channels(bot: Bot,
                                raffle: Raffle) -> None:
    config: Config = load_config()

    date = raffle.end_date.strftime("%d.%m.%Y")
    time = raffle.end_date.strftime("%H:%M")
    text = f"{raffle.description}\n\nЗаканчивается {date} в {time}"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=raffle.title,
                url=f"https://t.me/{config.reg_tg_bot.username}?"
                    f"start={raffle.id}"
            )]
        ]
    )

    for channel in raffle.raffle_channels:
        try:
            if raffle.photo_id:
                await bot.send_photo(channel.channel.chat_id,
                                     photo=raffle.photo_id,
                                     caption=text,
                                     reply_markup=keyboard)
            elif raffle.video_id:
                await bot.send_video(channel.channel.chat_id,
                                     video=raffle.video_id,
                                     caption=text,
                                     reply_markup=keyboard)
            else:
                await bot.send_message(channel.channel.chat_id,
                                       text=text,
                                       reply_markup=keyboard)
        except Exception as err:
            logger.error(f"Error send mail to channel/group "
                         f"{channel.channel.chat_id} with id "
                         f"{channel.channel.chat_id}: {err}")

    try:
        if raffle.photo_id:
            await bot.send_photo(config.tg_bot.channels,
                                 photo=raffle.photo_id,
                                 caption=text,
                                 reply_markup=keyboard)
        elif raffle.video_id:
            await bot.send_video(config.tg_bot.channels,
                                 video=raffle.video_id,
                                 caption=text,
                                 reply_markup=keyboard)
        else:
            await bot.send_message(config.tg_bot.channels,
                                   text=text,
                                   reply_markup=keyboard)
    except Exception as err:
        logger.error(f"Error send mail to channel/group "
                     f"{config.tg_bot.channels}: {err}")
