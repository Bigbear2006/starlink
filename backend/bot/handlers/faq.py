from aiogram import F, Router
from aiogram.types import Message, CallbackQuery

router = Router()


# @router.message(F.text == 'FAQ')
@router.callback_query(F.data == 'faq_command')
async def faq(query: CallbackQuery):
    await query.message.answer(
        'Правила активации и оплаты спутниковой тарелки:\n\n'

        '1. Активация\n'
        '• Активация тарелки производится в течение 24 часов '
        'с момента поступления оплаты.\n'
        '• В момент активации тарелка не должна быть подключена к сети.\n\n'

        '2. Оплата и повторное подключение\n'
        '• Если абонентская плата не внесена вовремя, повторное подключение '
        'осуществляется в течение 24 часов после полного погашения '
        'задолженности.\n'
        '• В случае отключения тарелки за неуплату, при повторном подключении '
        'необходимо оплатить весь период с момента отключения до фактической '
        'даты подключения. Частичная оплата не предусмотрена.\n\n'

        '3. Напоминание о платеже\n'
        '• Напоминание о необходимости оплаты направляется за 2-3 дня '
        'до фактической даты отключения.\n'
        '• Уведомление отправляется на номер КИТ (идентификатор тарелки).\n'
        'Такой порядок делает правила логичными, '
        'понятными и последовательными.',
    )
