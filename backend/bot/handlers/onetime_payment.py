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


@router.callback_query(F.data == 'onetime_payment_command')
async def onetime_payment(query: CallbackQuery, state: FSMContext):
    client = await Client.objects.aget(pk=query.message.chat.id)
    if not client.kit_number:
        await query.message.answer(
            'Сначала авторизуйтесь по KIT номеру тарелки.',
        )
        return

    await state.set_state(ConnectionState.form_url)
    await query.message.edit_text(
        f'Сумма единоразового платежа {settings.ONETIME_PAYMENT_PRICE} ₽',
        reply_markup=one_button_keyboard(
            text='Оплатить',
            callback_data='pay_onetime',
            back_button_data='switch_to_menu_kb',
        ),
    )


@router.callback_query(
    F.data == 'pay_onetime',
    StateFilter(ConnectionState.form_url),
)
async def pay_onetime(query: CallbackQuery, state: FSMContext):
    client = await Client.objects.aget(pk=query.message.chat.id)
    description = f'Оплата единоразового платежа {client.kit_number}'
    order_data = await alfa.register_order(
        settings.ONETIME_PAYMENT_PRICE * 100,
        description,
    )

    payment = await Payment.objects.acreate(
        amount=settings.ONETIME_PAYMENT_PRICE,
        description=description,
        order_id=order_data['orderId'],
        status=PaymentStatusChoices.REGISTERED,
        type=PaymentTypeChoices.ONETIME_PAYMENT,
        date=datetime.now(settings.TZ),
        client_id=query.message.chat.id,
    )

    await state.update_data(
        order_id=order_data['orderId'],
        form_url=order_data['formUrl'],
        payment_pk=payment.pk,
    )

    await state.set_state(ConnectionState.check_payment)
    await query.message.edit_text(
        f'Ваша ссылка на оплату:\n{order_data["formUrl"]}',
        reply_markup=one_button_keyboard(
            text='Я оплатил',
            callback_data='check_onetime_payment',
        ),
    )


@router.callback_query(
    F.data == 'check_onetime_payment',
    StateFilter(ConnectionState.check_payment),
)
async def check_onetime_payment(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = await alfa.get_order_status(data['order_id'])

    await Payment.objects.filter(pk=data['payment_pk']).aupdate(
        status=order_data.get('OrderStatus', 0),
        date=datetime.now(settings.TZ),
    )

    if order_data.get('OrderStatus', 0) == PaymentStatusChoices.SUCCESS:
        await Client.objects.filter(pk=query.message.chat.id).aupdate(
            onetime_payment=True,
        )
        await query.message.edit_text(
            'Готово, вы внесли единоразовый платеж.',
            reply_markup=to_menu_kb,
        )
        await state.clear()
    else:
        await query.message.edit_text(
            'К сожалению, оплата не прошла.\n'
            f'Вы можете попробовать оплатить еще раз:\n{data["form_url"]}',
            reply_markup=to_menu_kb,
        )

