from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.db.models import Model


def one_button_keyboard(
        *,
        back_button_data: str = None,
        **kwargs
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(**kwargs)
    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)

    kb.adjust(1)
    return kb.as_markup()


async def keyboard_from_queryset(
        model: type[Model],
        prefix: str,
        *,
        back_button_data: str = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    async for obj in model.objects.all():
        kb.button(text=str(obj), callback_data=f'{prefix}_{obj.pk}')

    if back_button_data:
        kb.button(text='Назад', callback_data=back_button_data)

    kb.adjust(1)
    return kb.as_markup()
