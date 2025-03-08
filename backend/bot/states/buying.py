from aiogram.fsm.state import StatesGroup, State


class BuyingState(StatesGroup):
    fullname = State()
    phone = State()
    buying = State()
