from aiogram import Router, F
from aiogram.types import Message


router = Router()


@router.message(F.text == 'FAQ')
async def faq(msg: Message):
    await msg.answer('Часто задаваемые вопросы')
