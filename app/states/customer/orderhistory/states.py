from aiogram.fsm.state import State, StatesGroup


from ..states import MainState


class OrderHistoryList(StatesGroup):
    _parent = MainState
    _STATE_FUNCTION = None
    main = State()


class OrderHistoryView(StatesGroup):
    _parent = OrderHistoryList
    _STATE_FUNCTION = None
    main = State()
