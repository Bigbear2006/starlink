from datetime import datetime

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.api import alfa
from bot.keyboards.inline import to_menu_kb
from bot.keyboards.utils import one_button_keyboard
from bot.settings import settings
from bot.states import ConnectionState
from starlink.models import (
    Client,
    Payment,
    PaymentStatusChoices,
    PaymentTypeChoices,
)

router = Router()


@router.callback_query(F.data == 'connect_command')
async def connect(query: CallbackQuery, state: FSMContext):
    client = await Client.objects.aget(pk=query.message.chat.id)
    if not client.kit_number:
        await query.message.answer(
            'Сначала авторизуйтесь по KIT номеру тарелки.',
        )
        return

    await state.set_state(ConnectionState.form_url)
    await query.message.edit_text(
        'Подключение тарелки стоит 5000 ₽',
        reply_markup=one_button_keyboard(
            text='Оплатить',
            callback_data='pay_connection',
            back_button_data='switch_to_menu_kb',
        ),
    )


@router.callback_query(
    F.data == 'pay_connection',
    StateFilter(ConnectionState.form_url),
)
async def pay_connection(query: CallbackQuery, state: FSMContext):
    client = await Client.objects.aget(pk=query.message.chat.id)
    description = f'Подключение тарелки {client.kit_number}'
    order_data = await alfa.register_order(5000 * 100, description)

    payment = await Payment.objects.acreate(
        amount=5000,
        description=description,
        order_id=order_data['orderId'],
        status=PaymentStatusChoices.REGISTERED,
        type=PaymentTypeChoices.CONNECTION,
        date=datetime.now(settings.TZ),
        client_id=query.message.chat.id,
    )

    await state.update_data(
        order_id=order_data['orderId'],
        payment_pk=payment.pk,
    )

    await state.set_state(ConnectionState.check_payment)
    await query.message.edit_text(
        f'Ваша ссылка на оплату:\n{order_data["formUrl"]}',
        reply_markup=one_button_keyboard(
            text='Я оплатил',
            callback_data='check_connection_payment',
        ),
    )


@router.callback_query(
    F.data == 'check_connection_payment',
    StateFilter(ConnectionState.check_payment),
)
async def check_payment(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    client = await Client.objects.aget(pk=query.message.chat.id)
    order_data = await alfa.get_order_status(data['order_id'])

    await Payment.objects.filter(pk=data['payment_pk']).aupdate(
        status=order_data.get('OrderStatus', 0),
        date=datetime.now(settings.TZ),
    )

    if order_data.get('OrderStatus', 0) == PaymentStatusChoices.SUCCESS:
        text = f'Подключение тарелки {client.kit_number}.\n'
        if query.message.from_user.username:
            text += f'Юзернейм пользователя: @{query.message.chat.username}'

        await query.bot.send_message(settings.FORWARD_CHAT_ID, text)
        await query.message.answer(
            'Готово, вашу тарелку скоро подключат.',
            reply_markup=to_menu_kb,
        )
        await state.clear()
    else:
        await query.message.answer(
            'К сожалению, оплата не прошла.',
            reply_markup=to_menu_kb,
        )

