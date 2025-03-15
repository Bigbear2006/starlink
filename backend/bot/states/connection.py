from aiogram.fsm.state import State, StatesGroup


class ConnectionState(StatesGroup):
    form_url = State()
    check_payment = State()
