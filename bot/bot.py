import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fluentogram import TranslatorHub

from bot.dialogs import register_dialogs
from bot.handlers import register_handlers
from bot.middlewares import TranslatorRunnerMiddleware
from bot.utils import check_end_time_raffle
from config import Config

logger = logging.getLogger(__name__)


async def setup_scheduler(bot: Bot, sender_bot: Bot):
    scheduler = AsyncIOScheduler()

    scheduler.add_job(
        check_end_time_raffle,
        'cron',
        minute='*',
        args=[bot, sender_bot]
    )

    scheduler.start()


async def main(
        config: Config,
        translator_hub: TranslatorHub,
        sender_bot: Bot,
        storage: RedisStorage | MemoryStorage = MemoryStorage()
) -> None:
    bot: Bot = Bot(token=config.tg_bot.token,
                   default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp: Dispatcher = Dispatcher(storage=storage)

    dp.update.middleware(TranslatorRunnerMiddleware())

    register_handlers(dp)
    register_dialogs(dp)
    setup_dialogs(dp)

    try:
        await setup_scheduler(bot, sender_bot)
        await dp.start_polling(bot,
                               _translator_hub=translator_hub,
                               sender_bot=sender_bot)
    except Exception as err:
        logger.error(f"Bot don`t started: {err}")
