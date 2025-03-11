from aiogram.fsm.state import State, StatesGroup


class BuyingState(StatesGroup):
    fullname = State()
    phone = State()
    buying = State()
