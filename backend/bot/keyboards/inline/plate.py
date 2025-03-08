from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

plate_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Купить', callback_data='buy_plate')]
    ]
)
