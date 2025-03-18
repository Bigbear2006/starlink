from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.inline import to_menu_kb
from bot.states import AuthState
from starlink.models import Client

router = Router()


@router.callback_query(F.data == 'auth_command')
async def auth(query: CallbackQuery, state: FSMContext):
    client = await Client.objects.aget(pk=query.message.chat.id)

    text = (
        'Введите кит номер тарелки, чтобы авторизоваться.\n'
        'Пример: KIT12345\n'
    )
    if client.kit_number:
        text += f'Ваш текущий номер тарелки: {client.kit_number}'

    await query.message.answer(text)
    await state.set_state(AuthState.plate_number)


@router.message(F.text, StateFilter(AuthState.plate_number))
async def set_plate_number(msg: Message, state: FSMContext):
    kit_number = msg.text.strip().upper()
    await Client.objects.filter(pk=msg.from_user.id)\
        .aupdate(kit_number=kit_number)

    await msg.answer(
        f'Вы успешно авторизовались по номеру тарелки {msg.text.upper()}',
        reply_markup=to_menu_kb,
    )
    await state.clear()

