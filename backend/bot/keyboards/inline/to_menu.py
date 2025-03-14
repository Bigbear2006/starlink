from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

to_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='В меню', callback_data='to_menu_command')],
    ],
)
