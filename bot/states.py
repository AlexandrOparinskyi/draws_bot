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
    home = State()
    raffle = State()
    confirm_delete = State()
    preview = State()
    add_channels = State()
    add_channel_instruction = State()
    start_error = State()


class ActiveRaffleState(StatesGroup):
    home = State()
    raffle = State()
    finish_confirm = State()
    sub_channels = State()
    add_channel_instruction = State()


class CompletedRaffleState(StatesGroup):
    home = State()
    raffle = State()


class EditRaffleState(StatesGroup):
    changes = State()
    change_param = State()


class ChannelState(StatesGroup):
    home = State()
    instruction = State()
