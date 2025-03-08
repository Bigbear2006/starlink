from dataclasses import dataclass, field

from environs import Env

env = Env()
env.read_env()


@dataclass
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))

    FORWARD_CHAT_ID: str = field(default='-1002309981972')
    SUPPORT_CHAT_URL: str = field(default='https://t.me/')
    MANAGER_URL: str = field(default='https://t.me/')
