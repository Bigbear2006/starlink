from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

plate_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Купить', callback_data='buy_plate')],
    ],
)
