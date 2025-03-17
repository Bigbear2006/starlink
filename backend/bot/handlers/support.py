from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot.keyboards.inline import to_menu_kb
from bot.keyboards.utils import keyboard_from_queryset, one_button_keyboard
from bot.settings import settings
from starlink.models import SupportSection

router = Router()


@router.callback_query(F.data == 'support_command')
async def support(query: CallbackQuery, state: FSMContext):
    await state.update_data(support_section_message_id=None)

    await query.message.edit_text(
        'Разделы технической поддержки',
        reply_markup=await keyboard_from_queryset(
            SupportSection,
            'support_section',
            back_button_data='switch_to_menu_kb',
        ),
    )


@router.callback_query(F.data.startswith('support_section'))
async def solution(query: CallbackQuery):
    section = await SupportSection.objects.aget(
        pk=int(query.data.split('_')[-1]),
    )
    text = f'{section.reason}\n\n{section.solution}'

    kb = one_button_keyboard(
        text='Мне нужен менеджер',
        callback_data='manager_needed',
        back_button_data='support_command',
    )

    await query.message.edit_text(
        text, reply_markup=kb,
    )


@router.callback_query(F.data == 'manager_needed')
async def manager_needed(query: CallbackQuery):
    await query.message.answer(
        f'Телеграм аккаунт менеджера - {settings.MANAGER_URL}',
        reply_markup=to_menu_kb,
    )
