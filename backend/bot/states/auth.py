from aiogram.fsm.state import State, StatesGroup


class AuthState(StatesGroup):
    plate_number = State()
