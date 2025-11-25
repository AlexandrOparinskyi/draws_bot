from aiogram import Router, Bot
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram_dialog import DialogManager, StartMode

from bot.utils import get_raffle_by_id, get_user_by_id, create_user
from config import Config
from reg_bot.states import PlayerState
from reg_bot.utils import create_raffle_player, get_raffle_player

players_router = Router()


@players_router.message(CommandStart())
async def command_start(message: Message,
                        command: CommandObject,
                        dialog_manager: DialogManager,
                        check_bot: Bot,
                        config: Config):
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

    if len(command.args.split("_")) == 1:
        raffle_id = int(command.args[0])
        raffle = await get_raffle_by_id(raffle_id)

        if raffle is None:
            return

        flag = True
        unsubscribe_channels = []

        for channel in raffle.channels:
            member = await check_bot.get_chat_member(channel.chat_id,
                                                     message.from_user.id)
            if member.status == "left":
                unsubscribe_channels.append(channel.chat_id)
                flag = False

        member = await check_bot.get_chat_member(config.tg_bot.channels,
                                                 message.from_user.id)
        if member.status == "left":
            unsubscribe_channels.append(config.tg_bot.channels)
            flag = False

        if flag:
            player = await get_raffle_player(message.from_user.id,
                                       raffle_id)
            if player is None:
                await create_raffle_player(message.from_user.id,
                                           raffle_id)

            await dialog_manager.start(state=PlayerState.raffle,
                                       data={"raffle_id": raffle_id})
            return

        await dialog_manager.start(state=PlayerState.check_subscribe,
                                   data={"raffle_id": raffle_id,
                                         "channels": unsubscribe_channels})

    else:
        pass
        # Check a referral user