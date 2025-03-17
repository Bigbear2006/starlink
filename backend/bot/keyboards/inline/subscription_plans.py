from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from starlink.models import SubscriptionPlanChoices


def get_subscription_plans_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text='Назад', callback_data='switch_to_menu_kb')
    for value, label in SubscriptionPlanChoices.choices:
        kb.button(text=label, callback_data=value)

    kb.adjust(1)
    return kb.as_markup()


subscription_plans_kb = get_subscription_plans_keyboard()
