from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

unauthorized_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Купить', callback_data='buy_command')],
        [
            InlineKeyboardButton(
                text='Авторизоваться',
                callback_data='auth_command',
            ),
        ],
    ],
)
