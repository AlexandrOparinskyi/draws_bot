from environs import env
from dataclasses import dataclass


@dataclass
class TgBot:
    token: str
    channel: str
    channel_username: str
    username: str
    admins: list[int]


@dataclass
class RegTgBot:
    token: str
    username: str
    media_chat: int


@dataclass
class Db:
    host: str
    port: str
    name: str
    user: str
    password: str


@dataclass
class AdminPanel:
    username: str
    password: str
    secret_key: str


@dataclass
class RedisConfig:
    host: str
    port: int
    db: int


@dataclass
class RegRedisConfig:
    host: str
    port: int
    db: int


@dataclass
class Config:
    tg_bot: TgBot
    reg_tg_bot: RegTgBot
    db: Db
    admin_panel: AdminPanel
    redis: RedisConfig
    reg_redis: RegRedisConfig


def load_config(path: str | None = None) -> Config:
    """Load the config"""
    env.read_env(path)
    return Config(
        tg_bot=TgBot(
            token=env.str("BOT_TOKEN"),
            channel=env.int("CHANNELS"),
            channel_username=env.str("CHANNEL_USERNAME"),
            username=env.str("BOT_USERNAME"),
            admins=[int(i) for i in env.str("ADMINS").split(",")]
        ),
        reg_tg_bot=RegTgBot(
            token=env.str("REG_BOT_TOKEN"),
            username=env.str("REG_BOT_USERNAME"),
            media_chat=env.int("REG_MEDIA_CHAT")
        ),
        db=Db(
            host=env.str("DB_HOST", "localhost"),
            port=env.str("DB_PORT", "5432"),
            name=env.str("DB_NAME", "postgres"),
            user=env.str("DB_USER", "postgres"),
            password=env.str("DB_PASS", "postgres"),
        ),
        admin_panel=AdminPanel(
            username=env.str("ADMIN_USERNAME", "admin"),
            password=env.str("ADMIN_PASSWORD", "password"),
            secret_key=env.str("ADMIN_SECRET_KEY", "test_key")
        ),
        redis=RedisConfig(
            host=env.str("REDIS_HOST", "localhost"),
            port=env.int("REDIS_PORT", 6379),
            db=env.int("REDIS_DB", 0),
        ),
        reg_redis=RegRedisConfig(
            host=env.str("REG_REDIS_HOST", "localhost"),
            port=env.int("REG_REDIS_PORT", 6379),
            db=env.int("REG_REDIS_DB", 1),
        )
    )


MAX_RAFFLE_TITLE_LENGTH = 50
MAX_RAFFLE_DESCRIPTION_LENGTH = 1500
