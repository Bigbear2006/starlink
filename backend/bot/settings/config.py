import json
from dataclasses import dataclass, field

from environs import Env
from pytz import timezone

env = Env()
env.read_env()


def load_kit_numbers_list():
    with open('kit_numbers.json') as f:
        kit_numbers = json.load(f)
    return kit_numbers


@dataclass
class Settings:
    BOT_TOKEN: str = field(default_factory=lambda: env('BOT_TOKEN'))
    REDIS_URL: str = field(default_factory=lambda: env('REDIS_URL'))

    ALFA_BASE_URL: str = field(default_factory=lambda: env('ALFA_BASE_URL'))
    ALFA_USERNAME: str = field(default_factory=lambda: env('ALFA_USERNAME'))
    ALFA_PASSWORD: str = field(default_factory=lambda: env('ALFA_PASSWORD'))
    ALFA_RETURN_URL: str = field(
        default_factory=lambda: env('ALFA_RETURN_URL'),
    )

    FORWARD_CHAT_ID: str = field(default='-1002309981972')
    MANAGER_URL: str = field(default='@maxxx190286')
    KIT_NUMBERS_LIST: list[str] = field(default_factory=load_kit_numbers_list)

    DATE_FMT: str = field(default='%d.%m.%Y %H:%M')
    SHORT_TIME_FMT: str = field(default='%H:%M')
    TZ: timezone = field(
        default_factory=lambda: timezone('Europe/Moscow'),
    )
