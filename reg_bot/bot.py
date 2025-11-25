import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from fluentogram import TranslatorHub

from reg_bot.dialogs import register_dialogs
from reg_bot.handlers import register_handlers
from bot.middlewares import TranslatorRunnerMiddleware
from config import Config

logger = logging.getLogger(__name__)


async def main(
        config: Config,
        translator_hub: TranslatorHub,
        check_bot: Bot,
        storage: RedisStorage | MemoryStorage = MemoryStorage()
) -> None:
    bot: Bot = Bot(token=config.reg_tg_bot.token,
                   default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp: Dispatcher = Dispatcher(storage=storage)

    dp.update.middleware(TranslatorRunnerMiddleware())

    register_handlers(dp)
    register_dialogs(dp)
    setup_dialogs(dp)

    try:
        await dp.start_polling(bot,
                               _translator_hub=translator_hub,
                               check_bot=check_bot,
                               config=config)
    except Exception as err:
        logger.error(f"Bot don`t started: {err}")
