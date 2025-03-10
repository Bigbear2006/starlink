import json
from dataclasses import dataclass, field

from environs import Env

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

    FORWARD_CHAT_ID: str = field(default='-1002309981972')
    MANAGER_URL: str = field(default='@maxxx190286')
    KIT_NUMBERS_LIST: list[str] = field(default_factory=load_kit_numbers_list)
