
from typing import Optional
from uuid import uuid4

from aiogram import Bot
from aiogram.types import BufferedInputFile

from config import Config


async def transfer_file_if_needed(original_file_id: str,
                                  original_bot: Bot,
                                  target_bot: Bot,
                                  config: Config,
                                  file_type: str) -> Optional[str]:
    """
    Передает файл между ботами и возвращает новый file_id
    """
    try:
        # Скачиваем файл
        file = await original_bot.get_file(original_file_id)
        downloaded_file = await original_bot.download_file(file.file_path)

        # Определяем тип файла
        file_extension = file.file_path.split('.')[-1] if file.file_path else 'jpg'

        # Создаем BufferedInputFile
        buffered_file = BufferedInputFile(
            downloaded_file.read(),
            filename=f"raffle_media_{str(uuid4())[:4]}.{file_extension}"
        )

        # Загружаем целевым ботом
        if file_type == "photo":
            message = await target_bot.send_photo(
                chat_id=config.reg_tg_bot.media_chat,
                photo=buffered_file
            )
            return message.photo[-1].file_id
        else:  # video
            message = await target_bot.send_video(  # Используем send_video для видео
                chat_id=config.reg_tg_bot.media_chat,
                video=buffered_file
            )
            return message.video.file_id

    except Exception as err:
        print(f"Error transferring file: {err}")
