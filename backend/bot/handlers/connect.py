from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.api import alfa
from bot.keyboards.utils import one_button_keyboard
from bot.settings import settings
from starlink.models import Client, PaymentStatusChoices

router = Router()


@router.message(Command('connect'))
@router.message(F.text == 'Подключение тарелки')
async def connect(msg: Message):
    await msg.answer(
        'Подключение тарелки стоит 5000 ₽',
        reply_markup=one_button_keyboard(
            text='Оплатить',
            callback_data='pay_connection',
        ),
    )


@router.callback_query(F.data == 'pay_connection')
async def pay_connection(query: CallbackQuery, state: FSMContext):
    order_data = await alfa.register_order(5000 * 100)

    await state.update_data(order_id=order_data['orderId'])
    await query.message.answer(
        f'Ваша ссылка на оплату. {order_data["formUrl"]}',
        reply_markup=one_button_keyboard(
            text='Я оплатил',
            callback_data='check_connection_payment',
        ),
    )


@router.callback_query(F.data == 'check_connection_payment')
async def check_payment(query: CallbackQuery, state: FSMContext):
    client = await Client.objects.aget(pk=query.message.chat.id)
    order_data = await alfa.get_order_status(await state.get_value('order_id'))

    if order_data.get('OrderStatus', 0) == PaymentStatusChoices.SUCCESS:
        text = f'Подключение тарелки {client.kit_number}.\n'
        if query.message.from_user.username:
            text += f'Юзернейм пользователя: @{query.message.chat.username}'

        await query.bot.send_message(settings.FORWARD_CHAT_ID, text)
        await query.message.answer('Готово, вашу тарелку скоро подключат.')
        await state.clear()
    else:
        await query.message.answer(
            'К сожалению, оплата не прошла.',
        )

