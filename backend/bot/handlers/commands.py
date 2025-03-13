from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.reply import menu_kb
from bot.loader import logger
from starlink.models import Client

router = Router()


@router.message(Command('start'))
async def start(msg: Message):
    client, created = await Client.objects.create_or_update_from_tg_user(
        msg.from_user,
    )
    if created:
        logger.info(f'New client {client} id={client.pk} was created')
    else:
        logger.info(f'Client {client} id={client.pk} was updated')

    await msg.answer(
        f'Привет, {msg.from_user.full_name}!\n'
        f'Я бот для покупки и обслуживания тарелок Starlink.',
        reply_markup=menu_kb,
    )


@router.message(Command('menu'))
async def menu(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer('Вы перешли в главное меню.', reply_markup=menu_kb)
