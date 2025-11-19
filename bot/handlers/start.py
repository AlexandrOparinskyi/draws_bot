from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from bot.states import UserState
from bot.utils import get_user_by_id, create_user

start_router = Router()


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
