from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message


router = Router()


@router.message(Command('connect'))
async def connect(msg: Message):
    pass


@router.message(Command('info'))
async def connection_info(msg: Message):
    pass
