import logging

from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, ErrorEvent
from aiogram_dialog import DialogManager, StartMode
from aiogram_dialog.api.exceptions import UnknownIntent

from bot.utils import get_raffle_by_id, get_user_by_id, create_user
from config import Config
from database import RaffleTypeEnum
from reg_bot.states import PlayerState
from reg_bot.utils import (create_raffle_player, get_raffle_player,
                           check_all_subscriptions_parallel)

players_router = Router()
logger = logging.getLogger(__name__)


@players_router.errors()
async def handle_unknown_intent(event: ErrorEvent):
    if isinstance(event.exception, UnknownIntent):
        await event.update.callback_query.answer("Сессия устарела. Введите команду /start",
                                                 show_alert=True)
        return True


@players_router.message(CommandStart())
async def command_start(message: Message,
                        command: CommandObject,
                        dialog_manager: DialogManager,
                        check_bot: Bot,
                        config: Config):
    user_id = message.from_user.id

    if message.from_user.is_bot:
        return
    try:
        user = await get_user_by_id(message.from_user.id)
        if user is None:
            await create_user(message.from_user.id,
                              message.from_user.username,
                              message.from_user.first_name,
                              message.from_user.last_name)

        if not command.args:
            await dialog_manager.start(state=PlayerState.home,
                                       mode=StartMode.RESET_STACK)
            return

        args_parts = command.args.split("_")
        raffle_id = int(args_parts[0])
        ref_parent = int(args_parts[1]) if len(args_parts) > 1 else None

        raffle = await get_raffle_by_id(raffle_id)
        if raffle is None:
            await message.answer("❌ Розыгрыш не найден")
            return

        if raffle.raffle_type == RaffleTypeEnum.COMPLETED:
            await message.answer("🏁 Этот розыгрыш уже завершен")
            return

        check_result = await check_all_subscriptions_parallel(
            check_bot=check_bot,
            user_id=user_id,
            channels=raffle.channels,
            main_channel_id=config.tg_bot.channel
        )

        if check_result["all_subscribed"]:
            player = await get_raffle_player(user_id, raffle_id)
            if player is None:
                await create_raffle_player(user_id, raffle_id, ref_parent)

            await dialog_manager.start(
                state=PlayerState.raffle,
                data={"raffle_id": raffle_id}
            )
        else:
            await dialog_manager.start(
                state=PlayerState.check_subscribe,
                data={
                    "raffle_id": raffle_id,
                    "channels": check_result["unsubscribed_channels"],
                    "main_channel": check_result["main_channel_subscribed"],
                    "ref_parent": ref_parent
                }
            )

    except Exception as e:
        logger.error(f"Error in command_start: {e}")
        await message.answer("⚠️ Ошибка")


@players_router.callback_query(F.data == "back_to_raffle")
async def back_to_raffle(callback: CallbackQuery,
                         dialog_manager: DialogManager):
    await dialog_manager.start(state=PlayerState.raffle,
                               data=dialog_manager.dialog_data)
