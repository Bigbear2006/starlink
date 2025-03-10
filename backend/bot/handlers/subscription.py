from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

pricing = {
    'standard': {
        'text': 'Стандарт - 15 000 ₽/мес.',
    },
    'flat': {
        'text': 'Флэт - 63 000 ₽/мес.',
    },
    'global': {
        'text': 'Глобал - 49 000 ₽/мес.',
    },
}


@router.message(Command('subscription'))
@router.message(F.text == 'Сроки подключения и абонентская плата')
async def subscription_info(msg: Message):
    kb = InlineKeyboardBuilder()
    for k, v in pricing.items():
        kb.button(text=v['text'], callback_data=k)
    kb.adjust(1)

    await msg.answer('Выберите тариф:', reply_markup=kb.as_markup())
