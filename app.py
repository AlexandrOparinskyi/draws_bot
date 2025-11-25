import asyncio
import json
import logging
from datetime import datetime, date
from typing import Any

from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from I18N import create_translator_hub
from config import Config, load_config
from bot import bot
from reg_bot import reg_bot

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] #%(levelname)-8s %(filename)s:'
           '%(lineno)d - %(name)s - %(message)s'
)


def custom_json_dumps(obj: Any) -> str:
    """Custom serialization for datetime"""

    def default_encoder(o):
        if isinstance(o, (datetime, date)):
            return {"__type__": "datetime", "value": o.strftime("%d.%m.%Y %H:%M")}
        return str(o)

    return json.dumps(obj, default=default_encoder, ensure_ascii=False)


def custom_json_loads(data: str) -> Any:
    """Custom deserialization with datetime recovery"""

    def object_hook(obj):
        if "__type__" in obj and obj["__type__"] == "datetime":
            return datetime.strptime(obj.get("value"), "%d.%m.%Y %H:%M")
        return obj

    result = json.loads(data, object_hook=object_hook)
    return result if isinstance(result, dict) else {}


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
        key_builder=DefaultKeyBuilder(with_destiny=True, prefix='bot_fsm'),
        json_loads=custom_json_loads,
        json_dumps=custom_json_dumps
    )

    reg_redis_client = Redis(
        host=config.reg_redis.host,
        port=config.reg_redis.port,
        db=config.reg_redis.db,
        decode_responses=False
    )
    reg_storage = RedisStorage(
        reg_redis_client,
        key_builder=DefaultKeyBuilder(with_destiny=True, prefix='r_bot_fsm'),
        json_loads=custom_json_loads,
        json_dumps=custom_json_dumps
    )

    await asyncio.gather(
        bot(
            config,
            translator_hub,
            storage
        ),
        reg_bot(
            config,
            translator_hub,
            reg_storage
        )
    )


if __name__ == "__main__":
    asyncio.run(main())
