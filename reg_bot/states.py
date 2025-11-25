from aiogram.fsm.state import StatesGroup, State


class PlayerState(StatesGroup):
    home = State()
    raffle = State()
    check_subscribe = State()
    invite = State()
