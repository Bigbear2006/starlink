from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards.utils import keyboard_from_queryset, one_button_keyboard
from bot.settings import settings
from starlink.models import SupportSection

router = Router()


@router.message(Command('support'))
@router.message(F.text == 'Техническая поддержка')
async def support(msg: Message, state: FSMContext):
    await state.update_data(support_section_message_id=None)

    await msg.answer(
        'Разделы технической поддержки',
        reply_markup=await keyboard_from_queryset(
            SupportSection,
            'support_section',
        ),
    )


@router.callback_query(F.data.startswith('support_section'))
async def solution(query: CallbackQuery, state: FSMContext):
    support_section_message_id = await state.get_value(
        'support_section_message_id',
    )
    section = await SupportSection.objects.aget(
        pk=int(query.data.split('_')[-1]),
    )
    text = f'{section.reason}\n\n{section.solution}'
    kb = one_button_keyboard(
        text='Мне нужен менеджер',
        callback_data='manager_needed',
    )

    if support_section_message_id:
        try:
            await query.bot.edit_message_text(
                text,
                query.message.business_connection_id,
                query.message.chat.id,
                support_section_message_id,
                reply_markup=kb,
            )
        except TelegramBadRequest:
            pass
    else:
        support_section_message = await query.message.answer(
            text, reply_markup=kb,
        )
        await state.update_data(
            support_section_message_id=support_section_message.message_id,
        )


@router.callback_query(F.data == 'manager_needed')
async def manager_needed(query: CallbackQuery):
    await query.message.answer(
        f'Телеграм аккаунт менеджера - {settings.MANAGER_URL}\n'
        f'Выйти в меню - /menu',
    )
