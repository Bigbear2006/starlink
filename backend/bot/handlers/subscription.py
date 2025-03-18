from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from django.core.exceptions import ObjectDoesNotExist

from bot.api import alfa
from bot.keyboards.inline import subscription_plans_kb, to_menu_kb
from bot.keyboards.utils import one_button_keyboard
from bot.settings import settings
from bot.states import SubscriptionState
from starlink.models import (
    Client,
    Payment,
    PaymentStatusChoices,
    PaymentTypeChoices,
    SubscriptionPlanChoices,
)

router = Router()


@router.callback_query(F.data == 'subscription_command')
async def subscription_info(query: CallbackQuery, state: FSMContext):
    client = await Client.objects.aget(pk=query.message.chat.id)
    if not client.kit_number:
        await query.message.answer(
            'Сначала авторизуйтесь по KIT номеру тарелки.',
        )
        return

    if client.subscription_end:
        days_count = 30
        plan = SubscriptionPlanChoices(client.subscription_plan).label

        remaining_days = (
                client.subscription_end - datetime.now(settings.TZ)
        ).days

        subscription_end_str = datetime.strftime(
            client.subscription_end.astimezone(settings.TZ),
            settings.DATE_FMT,
        )
        subscription_end_time_str = datetime.strftime(
            client.subscription_end.astimezone(settings.TZ),
            settings.SHORT_TIME_FMT,
        )

        text = f'Ваш тариф {plan}.\n\n'

        try:
            last_payment = await Payment.objects.filter(
                client=client,
                status=PaymentStatusChoices.SUCCESS,
                type=PaymentTypeChoices.SUBSCRIPTION,
            ).alatest('date')

            last_payment_str = datetime.strftime(
                last_payment.date.astimezone(settings.TZ),
                settings.DATE_FMT,
            )

            text += (
                f'Дата последнего продления подписки: {last_payment_str}.\n'
            )
        except ObjectDoesNotExist:
            pass

        if remaining_days < 0:
            text += (
                f'Ваша подписка закончилась {subscription_end_str}.\n'
                f'Ваш платеж просрочен на {-remaining_days} дней.'
            )
            days_count += -remaining_days
        elif remaining_days == 0:
            text += (
                f'Ваша подписка заканчивается сегодня в '
                f'{subscription_end_time_str}'
            )
        else:
            text += (
                f'Ваша подписка закончится {subscription_end_str} '
                f'(через {remaining_days} дней)'
            )

        await state.update_data(
            subscription_plan=client.subscription_plan,
            days_count=days_count,
        )

        await query.message.edit_text(
            text,
            reply_markup=one_button_keyboard(
                text='Продлить',
                callback_data='prolong_subscription',
                back_button_data='switch_to_menu_kb'
            ),
        )
    else:
        await state.set_state(SubscriptionState.form_url)
        await query.message.edit_text(
            'Выберите тариф:',
            reply_markup=subscription_plans_kb,
        )


@router.callback_query(
    F.data.in_(SubscriptionPlanChoices.values),
    StateFilter(SubscriptionState.form_url),
)
async def pay_subscription_plan(query: CallbackQuery):
    plan = SubscriptionPlanChoices(query.data)
    await query.message.edit_text(
        f'Вы выбрали тариф {plan.label}',
        reply_markup=one_button_keyboard(
            text='Оплатить',
            callback_data=f'pay_{plan.value}',
            back_button_data='subscription_command',
        )
    )


@router.callback_query(
    F.data.startswith('pay_'),
    StateFilter(SubscriptionState.form_url),
)
async def pay_subscription_plan(query: CallbackQuery, state: FSMContext):
    plan = SubscriptionPlanChoices(query.data.split('_')[-1])
    client = await Client.objects.aget(pk=query.message.chat.id)
    description = f'Оплата подписки {plan.label} на 30 дней ' \
                  f'({client.kit_number})'
    order_data = await alfa.register_order(
        plan.get_price() * 100,
        description,
    )

    payment = await Payment.objects.acreate(
        amount=plan.get_price(),
        description=description,
        order_id=order_data['orderId'],
        status=PaymentStatusChoices.REGISTERED,
        type=PaymentTypeChoices.SUBSCRIPTION,
        date=datetime.now(settings.TZ),
        client_id=query.message.chat.id,
    )

    await state.update_data(
        subscription_plan=plan.value,
        order_id=order_data['orderId'],
        form_url=order_data['formUrl'],
        payment_pk=payment.pk,
    )

    await state.set_state(SubscriptionState.check_payment)
    await query.message.edit_text(
        f'Вы выбрали тариф {plan.label}.\n'
        f'Ваша ссылка на оплату:\n{order_data["formUrl"]}\n',
        reply_markup=one_button_keyboard(
            text='Я оплатил',
            callback_data='check_subscription_buying',
        ),
    )


@router.callback_query(
    F.data == 'check_subscription_buying',
    StateFilter(SubscriptionState.check_payment),
)
async def check_subscription_buying(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    order_data = await alfa.get_order_status(data['order_id'])

    await Payment.objects.filter(pk=data['payment_pk']).aupdate(
        status=order_data.get('OrderStatus', 0),
        date=datetime.now(settings.TZ),
    )

    if order_data.get('OrderStatus', 0) == PaymentStatusChoices.SUCCESS:
        now = datetime.now(settings.TZ)

        await Client.objects\
            .filter(pk=query.message.chat.id)\
            .aupdate(
                subscription_end=now + timedelta(days=30),
                subscription_plan=data['subscription_plan'],
            )

        await query.message.edit_text(
            f'Вы купили подписку '
            f'{SubscriptionPlanChoices(data["subscription_plan"]).label}.',
            reply_markup=to_menu_kb,
        )
        await state.clear()
    else:
        await query.message.edit_text(
            'К сожалению, оплата не прошла.'
            f'Вы можете попробовать оплатить еще раз:\n{data["form_url"]}',
            reply_markup=to_menu_kb,
        )


@router.callback_query(F.data == 'prolong_subscription')
async def prolong_subscription(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    plan = SubscriptionPlanChoices(data['subscription_plan'])
    days_count = data.get('days_count', 30)
    client = await Client.objects.aget(pk=query.message.chat.id)
    description = f'Продление подписки {plan.label} на {days_count} дней ' \
                  f'({client.kit_number})'

    order_data = await alfa.register_order(
        plan.get_price() * days_count / 30 * 100,
        description,
    )

    payment = await Payment.objects.acreate(
        amount=plan.get_price() * days_count / 30,
        description=description,
        order_id=order_data['orderId'],
        status=PaymentStatusChoices.REGISTERED,
        type=PaymentTypeChoices.SUBSCRIPTION,
        date=datetime.now(settings.TZ),
        client_id=query.message.chat.id,
    )

    await state.update_data(
        subscription_plan=plan.value,
        order_id=order_data['orderId'],
        form_url=order_data['formUrl'],
        payment_pk=payment.pk,
    )

    await state.set_state(SubscriptionState.check_payment)
    await query.message.edit_text(
        f'Ваш тариф: {plan.label}.\n'
        f'Ваша ссылка для оплаты:\n{order_data["formUrl"]}',
        reply_markup=one_button_keyboard(
            text='Я оплатил',
            callback_data='check_subscription_prolonging',
        ),
    )


@router.callback_query(
    F.data == 'check_subscription_prolonging',
    StateFilter(SubscriptionState.check_payment),
)
async def check_subscription_prolonging(
        query: CallbackQuery,
        state: FSMContext,
):
    data = await state.get_data()
    days_count = data.get('days_count', 30)
    order_data = await alfa.get_order_status(data['order_id'])

    await Payment.objects.filter(pk=data['payment_pk']).aupdate(
        status=order_data.get('OrderStatus', 0),
        date=datetime.now(settings.TZ),
    )

    if order_data.get('OrderStatus', 0) == PaymentStatusChoices.SUCCESS:
        client = await Client.objects.aget(pk=query.message.chat.id)
        sub_end = client.subscription_end

        await Client.objects\
            .filter(pk=query.message.chat.id)\
            .aupdate(subscription_end=sub_end + timedelta(days=days_count))

        await query.message.edit_text(
            f'Вы продлили подписку на {days_count} дней.',
            reply_markup=to_menu_kb,
        )
        await state.clear()
    else:
        await query.message.edit_text(
            'К сожалению, оплата не прошла.\n'
            f'Вы можете попробовать оплатить еще раз:\n{data["form_url"]}',
            reply_markup=to_menu_kb,
        )
