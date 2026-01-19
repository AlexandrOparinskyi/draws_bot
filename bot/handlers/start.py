from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ErrorEvent
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.api.exceptions import UnknownIntent

from bot.states import UserState
from bot.utils import get_user_by_id, create_user

start_router = Router()


@start_router.errors()
async def handle_unknown_intent(event: ErrorEvent):
    if isinstance(event.exception, UnknownIntent):
        await event.update.callback_query.answer("Сессия устарела. Введите команду /start",
                                                 show_alert=True)
        return True



@start_router.message(CommandStart())
async def command_start(message: Message,
                        dialog_manager: DialogManager):
    user_id = message.from_user.id

    if not await get_user_by_id(user_id):
        await create_user(user_id=user_id,
                          username=message.from_user.username,
                          first_name=message.from_user.first_name,
                          last_name=message.from_user.last_name)

    await dialog_manager.start(state=UserState.home,
                               mode=StartMode.RESET_STACK)
