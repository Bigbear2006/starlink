from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import get_menu_keyboard
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
        reply_markup=get_menu_keyboard(client),
    )


@router.callback_query(F.data == 'to_menu')
async def menu(query: CallbackQuery, state: FSMContext):
    client = await Client.objects.aget(pk=query.message.chat.id)
    await state.clear()
    await query.message.answer(
        'Вы перешли в главное меню.',
        reply_markup=get_menu_keyboard(client)
    )


@router.callback_query(F.data == 'switch_to_menu_kb')
async def menu(query: CallbackQuery, state: FSMContext):
    client = await Client.objects.aget(pk=query.message.chat.id)
    await state.clear()
    await query.message.edit_text(
        'Вы перешли в главное меню.',
        reply_markup=get_menu_keyboard(client),
    )
