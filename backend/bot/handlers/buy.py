from aiogram import Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InputMediaPhoto, ReplyKeyboardRemove
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.inline import check_payment_kb, plate_kb
from bot.settings import settings
from bot.states import BuyingState

router = Router()

plates = [
    {
        'id': 1,
        'model': 'Модель 1',
        'photo': 'https://placehold.jp/3d4070/ffffff/150x150.png?text=%D0%9C%D0%BE%D0%B4%D0%B5%D0%BB%D1%8C%201',
        'price': 100,
        'description': 'Описание модели 1',
    },
    {
        'id': 2,
        'model': 'Модель 2',
        'photo': 'https://placehold.jp/d92626/ffffff/150x150.png?text=%D0%9C%D0%BE%D0%B4%D0%B5%D0%BB%D1%8C%202',
        'price': 100,
        'description': 'Описание модели 2',
    },
    {
        'id': 3,
        'model': 'Модель 3',
        'photo': 'https://placehold.jp/26d94a/ffffff/150x150.png?text=%D0%9C%D0%BE%D0%B4%D0%B5%D0%BB%D1%8C%203',
        'price': 100,
        'description': 'Описание модели 3',
    },
]


@router.message(Command('buy'))
async def buy(msg: Message, state: FSMContext):
    await state.update_data(plate_message_id=None)

    kb = InlineKeyboardBuilder()
    for plate in plates:
        kb.button(text=plate['model'], callback_data=f'plate_{plate["id"]}')
    kb.adjust(1)

    await msg.answer('Тарелки', reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith('plate'))
async def display_plate(query: CallbackQuery, state: FSMContext):
    plate_id = int(query.data.split('_')[-1])
    plate = list(filter(lambda x: x['id'] == plate_id, plates))[0]

    await state.update_data(plate_id=plate_id)
    plate_message_id = await state.get_value('plate_message_id')

    media = plate['photo']
    caption = f'{plate["model"]}\n\n{plate["description"]}'

    if plate_message_id:
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
    else:
        plate_message = await query.message.reply_photo(
            media,
            caption,
            reply_markup=plate_kb,
        )
        await state.update_data(plate_message_id=plate_message.message_id)


@router.callback_query(F.data == 'buy_plate')
async def buy_plate(query: CallbackQuery, state: FSMContext):
    await query.message.answer('Укажите ФИО')
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

    await msg.answer('Ваша ссылка на оплату.', reply_markup=check_payment_kb)
    await state.set_state(BuyingState.buying)


@router.callback_query(F.data == 'check_payment', StateFilter(BuyingState.buying))
async def check_payment(query: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    plate = list(filter(lambda x: x['id'] == data['plate_id'], plates))[0]

    payment_completed = True
    if payment_completed:
        text = (
            f'Покупка {plate["model"]}\n\n'
            f'Данные покупателя:\n'
            f'Телефон: {data["phone"]}\n'
        )
        if query.message.from_user.username:
            text += f'Юзернейм: @{query.message.from_user.username}'

        await query.bot.send_message(settings.FORWARD_CHAT_ID, text)
        await query.message.answer(
            'Готово, в ближайшее время с вами свяжется менеджер '
            'для уточнения деталей доставки.',
            reply_markup=ReplyKeyboardRemove()
        )
        await state.clear()
    else:
        await query.message.answer(
            'К сожалению оплата не прошла.\n'
            'Нажмите /menu, чтобы вернуться в меню',
            reply_markup=ReplyKeyboardRemove()
        )

