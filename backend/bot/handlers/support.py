from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

router = Router()


@router.message(Command('connect'))
async def support(msg: Message):
    pass


@router.callback_query(F.data.startswith('support'))
async def solution(query: CallbackQuery):
    pass
