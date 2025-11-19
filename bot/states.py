from aiogram.fsm.state import StatesGroup, State


class UserState(StatesGroup):
    home = State()


class RaffleState(StatesGroup):
    title = State()
    description = State()
    media = State()
    end_date = State()
    winners_count = State()
    ref_system = State()
    show_result = State()


class CreatedRaffleState(StatesGroup):
    list_raffle = State()
    home = State()

