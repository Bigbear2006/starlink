from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

check_payment_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Я оплатил', callback_data='check_payment')]
    ]
)
