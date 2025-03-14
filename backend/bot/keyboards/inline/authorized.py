from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

authorized_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Купить тарелку',
                callback_data='buy_command',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Подключить тарелку',
                callback_data='connect_command',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Абонентская плата',
                callback_data='subscription_command',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Тех. поддержка',
                callback_data='support_command',
            ),
            InlineKeyboardButton(text='FAQ', callback_data='faq_command'),
        ],
    ],
)
