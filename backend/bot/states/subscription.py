from aiogram.fsm.state import State, StatesGroup


class SubscriptionState(StatesGroup):
    form_url = State()
    check_payment = State()
