from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from django import conf
from django.core.exceptions import ObjectDoesNotExist
from pytz import timezone

from bot.keyboards.inline import subscription_plans_kb
from bot.keyboards.utils import one_button_keyboard
from bot.settings import settings
from starlink.models import Payment, PaymentChoices, SubscriptionPlanChoices

router = Router()


@router.message(Command('subscription'))
@router.message(F.text == 'Сроки подключения и абонентская плата')
async def display_subscription_plans(msg: Message, state: FSMContext):
    try:
        earliest_payment = await Payment.objects.filter(
            client_id=msg.chat.id,
            status=PaymentChoices.SUCCESS,
        ).aearliest('date')

        last_payment = await Payment.objects.filter(
            client_id=msg.chat.id,
            status=PaymentChoices.SUCCESS,
        ).alatest('date')

        payments_count = await Payment.objects.filter(
            client_id=msg.chat.id,
            status=PaymentChoices.SUCCESS,
        ).acount()

        subscription_end: datetime = earliest_payment.date + \
                                     timedelta(days=30 * payments_count)
        remaining_days = (
                subscription_end -
                datetime.now(timezone(conf.settings.TIME_ZONE))
        ).days

        plan = SubscriptionPlanChoices(
            earliest_payment.subscription_plan,
        ).label

        last_payment_str = datetime.strftime(
            last_payment.date,
            settings.DATE_FMT,
        )

        await state.update_data(
            subscription_plan=earliest_payment.subscription_plan,
        )
        await msg.answer(
            f'Ваш тариф: {plan}\n'
            f'Дата последнего продления подписки: {last_payment_str}\n'
            f'Ваша подписка закончится '
            f'{datetime.strftime(subscription_end, settings.DATE_FMT)} '
            f'(через {remaining_days} дней)',
            reply_markup=one_button_keyboard(
                text='Продлить',
                callback_data='prolong_subscription',
            ),
        )
    except ObjectDoesNotExist:
        await msg.answer('Выберите тариф:', reply_markup=subscription_plans_kb)


@router.callback_query(F.data.in_(SubscriptionPlanChoices.values))
async def pay_subscription_plan(query: CallbackQuery, state: FSMContext):
    plan = SubscriptionPlanChoices(query.data)
    await state.update_data(subscription_plan=plan.value)
    await query.message.answer(
        f'Вы выбрали тариф {plan.label}.\nВаша ссылка для оплаты.',
        reply_markup=one_button_keyboard(
            text='Я оплатил',
            callback_data='check_subscription_buying',
        ),
    )


@router.callback_query(F.data == 'check_subscription_buying')
async def check_subscription_buying(query: CallbackQuery, state: FSMContext):
    check_payment = True
    if check_payment:
        await Payment.objects.acreate(
            client_id=query.message.chat.id,
            status=PaymentChoices.SUCCESS,
            subscription_plan=await state.get_value('subscription_plan'),
            date=datetime.now(timezone(conf.settings.TIME_ZONE)),
        )
        await query.message.answer('Вы купили подписку')
    else:
        await query.message.answer('К сожалению, оплата не прошла.')


@router.callback_query(F.data == 'prolong_subscription')
async def prolong_subscription(query: CallbackQuery):
    await query.message.answer(
        'Ваша ссылка для оплаты',
        reply_markup=one_button_keyboard(
            text='Я оплатил',
            callback_data='check_subscription_prolonging',
        ),
    )


@router.callback_query(F.data == 'check_subscription_prolonging')
async def check_subscription_prolonging(
        query: CallbackQuery,
        state: FSMContext,
):
    check_payment = True
    if check_payment:
        await Payment.objects.acreate(
            client_id=query.message.chat.id,
            status=PaymentChoices.SUCCESS,
            subscription_plan=await state.get_value('subscription_plan'),
            date=datetime.now(timezone(conf.settings.TIME_ZONE)),
        )
        await query.message.answer('Вы продлили подписку на 30 дней.')
    else:
        await query.message.answer('К сожалению, оплата не прошла.')
