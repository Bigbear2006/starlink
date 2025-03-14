from datetime import datetime
from urllib.parse import unquote

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    BufferedInputFile,
    CallbackQuery,
    InputMediaPhoto,
    Message,
)

from bot.api import alfa
from bot.keyboards.inline import plate_kb, to_menu_kb
from bot.keyboards.utils import keyboard_from_queryset, one_button_keyboard
from bot.settings import settings
from bot.states import BuyingState
from starlink.models import (
    Payment,
    PaymentStatusChoices,
    PaymentTypeChoices,
    Plate,
)

router = Router()


@router.callback_query(F.data == 'buy_command')
async def buy(query: CallbackQuery, state: FSMContext):
    await state.update_data(plate_message_id=None)

    await query.message.answer(
        'Тарелки',
        reply_markup=await keyboard_from_queryset(Plate, 'plate'),
    )


@router.callback_query(F.data.startswith('plate'))
async def display_plate(query: CallbackQuery, state: FSMContext):
    plate = await Plate.objects.aget(pk=int(query.data.split('_')[-1]))

    await state.update_data(plate_id=plate.pk)
    plate_message_id = await state.get_value('plate_message_id')

    media = BufferedInputFile.from_file(unquote(plate.photo.url.lstrip('/')))
    caption = (
        f'{plate.model}\n\n'
        f'Цена: {plate.price}\n'
        f'{plate.description}'
    )

    if plate_message_id:
        try:
            await query.bot.edit_message_media(
                InputMediaPhoto(
                    media=media,
                    caption=caption,
                ),
                query.message.business_connection_id,
                query.message.chat.id,
                plate_message_id,
                reply_markup=plate_kb,
            )
        except TelegramBadRequest:
            pass
    else:
        plate_message = await query.message.reply_photo(
            media,
            caption,
            reply_markup=plate_kb,
        )
        await state.update_data(plate_message_id=plate_message.message_id)


@router.callback_query(F.data == 'buy_plate')
async def buy_plate(query: CallbackQuery, state: FSMContext):
    await query.message.answer('Укажите имя (как к вам обращаться)')
    await state.set_state(BuyingState.fullname)


@router.message(F.text, StateFilter(BuyingState.fullname))
async def set_fullname(msg: Message, state: FSMContext):
    await state.update_data(fullname=msg.text)
    await msg.answer('Укажите номер телефона')
    await state.set_state(BuyingState.phone)


@router.message(F.contact | F.text, StateFilter(BuyingState.phone))
async def set_phone(msg: Message, state: FSMContext):
    if msg.contact:
        await state.update_data(phone=msg.contact.phone_number)
    else:
        await state.update_data(phone=msg.text)

    plate = await Plate.objects.aget(pk=await state.get_value('plate_id'))
    description = f'Покупка тарелки {plate.model}'
    order_data = await alfa.register_order(plate.price * 100, description)

    payment = await Payment.objects.acreate(
        amount=plate.price,
        description=description,
        order_id=order_data['orderId'],
        status=PaymentStatusChoices.REGISTERED,
        type=PaymentTypeChoices.BUYING,
        date=datetime.now(settings.TZ),
        client_id=msg.chat.id,
    )

    await state.update_data(
        order_id=order_data['orderId'],
        payment_pk=payment.pk,
    )

    await msg.answer(
        f'Ваша ссылка на оплату:\n{order_data["formUrl"]}',
        reply_markup=one_button_keyboard(
            text='Я оплатил',
            callback_data='check_buying_payment',
        ),
    )
    await state.set_state(BuyingState.buying)


@router.callback_query(
    F.data == 'check_buying_payment',
    StateFilter(BuyingState.buying),
)
async def check_buying_payment(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    plate = await Plate.objects.aget(pk=data['plate_id'])
    order_data = await alfa.get_order_status(data['order_id'])

    await Payment.objects.filter(pk=data['payment_pk']).aupdate(
        status=order_data.get('OrderStatus', 0),
        date=datetime.now(settings.TZ),
    )

    if order_data.get('OrderStatus', 0) == PaymentStatusChoices.SUCCESS:
        text = (
            f'Покупка тарелки {plate.model}\n\n'
            f'Данные покупателя:\n'
            f'Телефон: {data["phone"]}\n'
        )
        if query.message.from_user.username:
            text += f'Юзернейм: @{query.message.chat.username}'

        await query.bot.send_message(settings.FORWARD_CHAT_ID, text)
        await query.message.answer(
            'Готово, в ближайшее время с вами свяжется менеджер '
            'для уточнения деталей доставки.',
            reply_markup=to_menu_kb,
        )
        await state.clear()
    else:
        await query.message.answer(
            'К сожалению оплата не прошла.',
            reply_markup=to_menu_kb,
        )
