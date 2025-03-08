from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

after_auth_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Подключение тарелки')],
        [KeyboardButton(text='Сроки подключения и абонентская плата')],
        [KeyboardButton(text='Техническая поддержка')],
        [KeyboardButton(text='FAQ')],
    ],
    resize_keyboard=True,
)

