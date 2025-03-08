from aiogram.fsm.state import StatesGroup, State


class AuthState(StatesGroup):
    plate_number = State()
