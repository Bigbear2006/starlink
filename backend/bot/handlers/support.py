from urllib.parse import unquote

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, BufferedInputFile, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.keyboards.utils import keyboard_from_queryset, one_button_keyboard
from bot.settings import settings
from starlink.models import SupportSection

router = Router()


@router.callback_query(F.data == 'support_command')
async def support(query: CallbackQuery, state: FSMContext):
    await state.update_data(support_section_message_id=None)

    kb = InlineKeyboardBuilder.from_markup(
        await keyboard_from_queryset(
            SupportSection,
            'support_section',
        )
    )
    kb.button(text='Мне нужен менеджер', url=settings.MANAGER_URL)
    kb.button(text='Назад', callback_data='switch_to_menu_kb')
    kb.adjust(1)

    await query.message.edit_text(
        'Разделы технической поддержки',
        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data.startswith('support_section'))
async def solution(query: CallbackQuery, state: FSMContext):
    support_section_message_id = await state.get_value(
        'support_section_message_id',
    )
    section = await SupportSection.objects.aget(
        pk=int(query.data.split('_')[-1]),
    )

    media = BufferedInputFile.from_file(unquote(section.photo.url.lstrip('/')))
    caption = f'{section.reason}\n\n{section.solution}'
    kb = one_button_keyboard(
        text='Мне нужен менеджер',
        url=settings.MANAGER_URL,
        back_button_data='delete_support_section_message',
    )

    if support_section_message_id:
        try:
            await query.bot.edit_message_media(
                InputMediaPhoto(media=media, caption=caption),
                query.message.business_connection_id,
                query.message.chat.id,
                support_section_message_id,
                reply_markup=kb,
            )
        except TelegramBadRequest:
            pass
    else:
        support_section_message = await query.message.answer_photo(
            media,
            caption,
            reply_markup=kb,
        )
        await state.update_data(
            support_section_message_id=support_section_message.message_id,
        )


@router.callback_query(F.data == 'delete_support_section_message')
async def delete_support_section_message(query: CallbackQuery, state: FSMContext):
    await query.bot.delete_message(
        query.message.chat.id,
        await state.get_value('support_section_message_id'),
    )
    await state.update_data(support_section_message_id=None)
