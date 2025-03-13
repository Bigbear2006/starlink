from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Подключить тарелку')],
        [KeyboardButton(text='Сроки подключения и абонентская плата')],
        [
            KeyboardButton(text='Купить тарелку'),
            KeyboardButton(text='Авторизоваться'),
        ],
        [
            KeyboardButton(text='Техническая поддержка'),
            KeyboardButton(text='FAQ'),
        ],
    ],
    resize_keyboard=True,
)

