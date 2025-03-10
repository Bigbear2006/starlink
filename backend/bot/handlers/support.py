from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from starlink.models import SupportSection

router = Router()


@router.message(Command('support'))
@router.message(F.text == 'Техническая поддержка')
async def support(msg: Message, state: FSMContext):
    await state.update_data(support_section_message_id=None)

    kb = InlineKeyboardBuilder()
    sections = SupportSection.objects.all()
    async for section in sections:
        kb.button(text=section.reason[:50], callback_data=f'support_section_{section.pk}')
    kb.adjust(1)

    await msg.answer('Разделы технической поддержки', reply_markup=kb.as_markup())


@router.callback_query(F.data.startswith('support_section'))
async def solution(query: CallbackQuery, state: FSMContext):
    support_section_message_id = await state.get_value('support_section_message_id')
    section = await SupportSection.objects.aget(pk=int(query.data.split('_')[-1]))
    text = f'{section.reason}\n\n{section.solution}'

    if support_section_message_id:
        try:
            await query.bot.edit_message_text(
                text,
                query.message.business_connection_id,
                query.message.chat.id,
                support_section_message_id
            )
        except TelegramBadRequest:
            pass
    else:
        support_section_message = await query.message.answer(text)
        await state.update_data(
            support_section_message_id=support_section_message.message_id,
        )
