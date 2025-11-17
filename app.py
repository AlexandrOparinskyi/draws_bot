import asyncio

from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from I18N import create_translator_hub
from config import Config, load_config
from bot import bot


async def main() -> None:
    config: Config = load_config()
    translator_hub = create_translator_hub()

    redis_client = Redis(
        host=config.redis.host,
        port=config.redis.port,
        db=config.redis.db,
        decode_responses=False
    )
    storage = RedisStorage(
        redis_client,
        key_builder=DefaultKeyBuilder(with_destiny=True, prefix='bot_fsm')
    )

    await asyncio.gather(bot(
        config,
        translator_hub,
        storage
    ))


if __name__ == "__main__":
    asyncio.run(main())
