from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Model


def one_button_keyboard(
        *,
        back_button_data: str = None,
        **kwargs
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)
    kb.button(**kwargs)

    kb.adjust(1)
    return kb.as_markup()


async def keyboard_from_queryset(
        model: type[Model],
        prefix: str,
        *,
        back_button_data: str = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)

    async for obj in model.objects.all():
        kb.button(text=str(obj), callback_data=f'{prefix}_{obj.pk}')

    kb.adjust(1)
    return kb.as_markup()
