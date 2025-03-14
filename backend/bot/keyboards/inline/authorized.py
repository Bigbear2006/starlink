from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

authorized_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Подключить тарелку',
                callback_data='connect_command',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Сроки подключения и абонентская плата',
                callback_data='subscription_command',
            ),
        ],
        [
            InlineKeyboardButton(
                text='Техническая поддержка',
                callback_data='support_command'
            ),
        ],
        [InlineKeyboardButton(text='FAQ', callback_data='faq_command')],
    ],
)
