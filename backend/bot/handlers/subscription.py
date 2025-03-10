from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from django.core.exceptions import ObjectDoesNotExist

from bot.keyboards.inline import subscription_plans_kb
from bot.keyboards.utils import one_button_keyboard
from bot.settings.subscription_plans import subscription_plans
from starlink.models import Payment, PaymentChoices

router = Router()


@router.message(Command('subscription'))
@router.message(F.text == 'Сроки подключения и абонентская плата')
async def display_subscription_plans(msg: Message):
    try:
        last_payment = await Payment.objects.filter(
            client_id=msg.chat.id,
            status=PaymentChoices.SUCCESS,
        ).alatest('date')
        remaining_days = datetime.now() - last_payment.date

        await msg.answer(
            f'Дата последнего продления подписки: {last_payment.date}'
            f'Ваша подписка закончится {last_payment.date + timedelta(days=30)} '
            f'(через {remaining_days.days} дней)',
            reply_markup=one_button_keyboard(text='Продлить', callback_data='prolong_subscription')
        )
    except ObjectDoesNotExist:
        await msg.answer('Выберите тариф:', reply_markup=subscription_plans_kb)


@router.callback_query(F.data.in_(subscription_plans.keys()))
async def pay_subscription_plan(query: CallbackQuery):
    plan = subscription_plans[query.data]
    await query.message.answer(
        f'Вы выбрали тариф {plan}.\nВаша ссылка для оплаты.',
        reply_markup=one_button_keyboard(text='Я оплатил', callback_data='check_subscription_buying'),
    )


@router.callback_query(F.data == 'check_subscription_buying')
async def check_subscription_buying(query: CallbackQuery):
    check_payment = True
    if check_payment:
        await Payment.objects.acreate(
            client_id=query.message.chat.id,
            status=PaymentChoices.SUCCESS,
            date=datetime.now(),
        )
        await query.message.answer('Вы купили подписку')
    else:
        await query.message.answer('К сожалению, оплата не прошла.')


@router.callback_query(F.data == 'prolong_subscription')
async def prolong_subscription(query: CallbackQuery):
    await query.message.answer(
        'Ваша ссылка для оплаты',
        reply_markup=one_button_keyboard(text='Я оплатил', callback_data='check_subscription_prolonging'),
    )


@router.callback_query(F.data == 'prolong_subscription')
async def prolong_subscription(query: CallbackQuery):
    check_payment = True
    if check_payment:
        await Payment.objects.acreate(
            client_id=query.message.chat.id,
            status=PaymentChoices.SUCCESS,
            date=datetime.now(),
        )
        await query.message.answer('Вы продлили подписку на 30 дней.')
    else:
        await query.message.answer('К сожалению, оплата не прошла.')
