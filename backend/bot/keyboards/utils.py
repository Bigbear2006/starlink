from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Model


def one_button_keyboard(**kwargs) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(**kwargs)]],
    )


async def keyboard_from_queryset(
        model: type[Model],
        prefix: str,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    async for obj in model.objects.all():
        kb.button(text=str(obj), callback_data=f'{prefix}_{obj.pk}')
    kb.adjust(1)
    return kb.as_markup()
