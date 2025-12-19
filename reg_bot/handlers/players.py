from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager, StartMode

from bot.utils import get_raffle_by_id, get_user_by_id, create_user
from config import Config
from database import RaffleTypeEnum
from reg_bot.states import PlayerState
from reg_bot.utils import create_raffle_player, get_raffle_player

players_router = Router()


@players_router.message(CommandStart())
async def command_start(message: Message,
                        command: CommandObject,
                        dialog_manager: DialogManager,
                        check_bot: Bot,
                        config: Config):
    if message.from_user.is_bot:
        return

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

    raffle_id = int(command.args.split("_")[0])
    raffle = await get_raffle_by_id(raffle_id)

    if raffle is None:
        return

    if raffle.raffle_type == RaffleTypeEnum.COMPLETED:
        await message.answer("Розыгрыш завершен")
        return

    flag = True
    sub_main_channel = True
    unsubscribe_channels = []

    for channel in raffle.channels:
        try:
            member = await check_bot.get_chat_member(channel.chat_id,
                                                     message.from_user.id)
            if member.status == "left":
                unsubscribe_channels.append(channel.chat_id)
                flag = False
        except:
            flag = False
            unsubscribe_channels.append(channel.chat_id)

    try:
        member = await check_bot.get_chat_member(config.tg_bot.channel,
                                                 message.from_user.id)
        if member.status == "left":
            flag = False
            sub_main_channel = False
    except:
        flag = False
        sub_main_channel = False

    if flag:
        player = await get_raffle_player(message.from_user.id,
                                         raffle_id)
        if player is None:
            if len(command.args.split("_")) == 2:
                await create_raffle_player(message.from_user.id,
                                           raffle_id,
                                           int(command.args.split("_")[1]))
            else:
                await create_raffle_player(message.from_user.id,
                                           raffle_id)

        await dialog_manager.start(state=PlayerState.raffle,
                                   data={"raffle_id": raffle_id})
        return

    if len(command.args.split("_")) == 2:
        ref_parent = command.args.split("_")[1]
    else:
        ref_parent = None

    await dialog_manager.start(state=PlayerState.check_subscribe,
                               data={"raffle_id": raffle_id,
                                     "channels": unsubscribe_channels,
                                     "main_channel": sub_main_channel,
                                     "ref_parent": ref_parent})


@players_router.callback_query(F.data == "back_to_raffle")
async def back_to_raffle(callback: CallbackQuery,
                         dialog_manager: DialogManager):
    await dialog_manager.start(state=PlayerState.raffle,
                               data=dialog_manager.dialog_data)
