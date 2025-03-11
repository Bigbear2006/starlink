from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.reply import after_auth_kb
from bot.settings import settings
from bot.states import AuthState
from starlink.models import Client

router = Router()


@router.message(Command('auth'))
async def auth(msg: Message, state: FSMContext):
    client = await Client.objects.aget(pk=msg.from_user.id)

    text = (
        'Введите кит номер тарелки, чтобы авторизоваться.\n'
        'Пример: KIT12345\n'
    )
    if client.kit_number:
        text += f'Ваш текущий номер тарелки: {client.kit_number}'

    await msg.answer(text)
    await state.set_state(AuthState.plate_number)


@router.message(F.text, StateFilter(AuthState.plate_number))
async def set_plate_number(msg: Message, state: FSMContext):
    kit_number = msg.text.strip().upper()
    if kit_number in settings.KIT_NUMBERS_LIST:
        await Client.objects.filter(pk=msg.from_user.id)\
            .aupdate(kit_number=kit_number)
        await msg.answer(
            f'Вы успешно авторизовались по номеру тарелки {msg.text.upper()}',
            reply_markup=after_auth_kb,
        )
        await state.clear()
    else:
        await msg.answer(
            'Такого KIT номера нет. '
            'Попробуйте ещё раз или выйдите в главное меню - /menu',
        )
