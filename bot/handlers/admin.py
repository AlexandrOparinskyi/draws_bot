import asyncio
import logging

import aiofiles
from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BufferedInputFile

from bot.utils import get_all_users
from config import Config

admin_router = Router()
logger = logging.getLogger(__name__)


class SendState(StatesGroup):
    message = State()
    confirm = State()


@admin_router.message(Command(commands="send_mailing"))
async def send_mailing(message: Message,
                       config: Config):
    if message.from_user.id not in config.tg_bot.admins:
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Бот розыгрышей",
                callback_data="raffle_bot"
            ),
                InlineKeyboardButton(
                    text="Бот участников",
                    callback_data="players_bot"
                )],
            [InlineKeyboardButton(
                text="Оба бота",
                callback_data="two_bots"
            )]
        ]
    )
    await message.answer("Выберите вид рассылки", reply_markup=keyboard)


@admin_router.callback_query(lambda x: x.data in ["raffle_bot",
                                                  "players_bot",
                                                  "two_bots"])
async def create_message(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SendState.message)
    await state.update_data(send_type=callback.data)

    await callback.message.answer("Введите сообщение. Если хотите отправить "
                                  "фото или видео - прикрепите его")


@admin_router.message(StateFilter(SendState.message))
async def confirm_mailing(message: Message, state: FSMContext, bot: Bot):
    await state.set_state(SendState.confirm)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text="Подтвердить отправку",
                callback_data="confirm_mailing"
            )]
        ]
    )

    if message.photo:
        await bot.send_photo(message.from_user.id,
                             photo=message.photo[-1].file_id,
                             caption=message.caption,
                             reply_markup=keyboard)
        await state.update_data(photo_id=message.photo[-1].file_id,
                                text=message.caption)
        return
    else:
        await message.answer(message.text, reply_markup=keyboard)
        await state.update_data(text=message.text)


@admin_router.callback_query(StateFilter(SendState.confirm),
                             F.data == "confirm_mailing")
async def send_mailing_confirm(callback: CallbackQuery,
                               state: FSMContext,
                               config: Config,
                               bot: Bot,
                               sender_bot: Bot):
    data = await state.get_data()
    await state.clear()
    sender_type = data.get("send_type")
    users = await get_all_users()

    if sender_type == "raffle_bot":
        sender = [bot]
    elif sender_type == "players_bot":
        sender = [sender_bot]
    else:
        sender = [bot, sender_bot]

    if data.get("photo_id"):
        file = await bot.get_file(data.get("photo_id"))
        file_path = file.file_path
        file_exp = file_path.split(".")[-1]
        await bot.download_file(file_path, f"sender_file.{file_exp}")

        async with aiofiles.open(f"sender_file.{file_exp}", "rb") as file:
            file_bytes = await file.read()

        input_file = BufferedInputFile(file_bytes, filename="photo.jpg")
    else:
        input_file = None

    for num, user in enumerate(users):
        if user.id in config.tg_bot.admins:
            continue

        if num % 15 == 0:
            await asyncio.sleep(1)

        for send in sender:
            try:
                if data.get("photo_id"):
                    await send.send_photo(user.id,
                                          input_file,
                                          caption=data.get("text"))
                else:
                    await send.send_message(user.id, data.get("text"))
            except Exception as err:
                logger.error(f"Error send to {user.id}: {err}")

    await callback.message.answer("Отправка завершена")
