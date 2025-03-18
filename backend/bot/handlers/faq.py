from aiogram import F, Router
from aiogram.types import CallbackQuery

from bot.keyboards.utils import one_button_keyboard
from starlink.models import FAQ

router = Router()


@router.callback_query(F.data == 'faq_command')
async def faq(query: CallbackQuery):
    await query.message.edit_text(
        (await FAQ.objects.afirst()).text,
        reply_markup=one_button_keyboard(
            text='Назад',
            callback_data='switch_to_menu_kb',
        )
    )
