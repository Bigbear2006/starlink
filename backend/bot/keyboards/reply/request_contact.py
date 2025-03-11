from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

request_contact_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(
            text='Поделиться номером телефона',
            request_contact=True,
        )],
    ],
    resize_keyboard=True,
)

