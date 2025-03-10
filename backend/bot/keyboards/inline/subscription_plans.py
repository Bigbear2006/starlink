from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.settings.subscription_plans import subscription_plans


def get_subscription_plans_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for k, v in subscription_plans.items():
        kb.button(text=v['text'], callback_data=k)
    kb.adjust(1)
    return kb.as_markup()


subscription_plans_kb = get_subscription_plans_keyboard()
