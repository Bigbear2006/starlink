from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from starlink.models import Client


def get_authorized_keyboard(client: Client) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder(
        [
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
        ],
    )

    if not client.onetime_payment:
        kb.button(text='Единоразовый платеж', callback_data='onetime_payment_command')
    kb.adjust(1)

    kb.row(
        InlineKeyboardButton(
            text='Тех. поддержка',
            callback_data='support_command',
        ),
        InlineKeyboardButton(text='FAQ', callback_data='faq_command'),
    )
    return kb.as_markup()
