from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Купить тарелку')],
        [KeyboardButton(text='Авторизоваться')],
    ],
    resize_keyboard=True,
)

