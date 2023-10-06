from aiogram.fsm.state import State, StatesGroup


__all__ = (
    'MainState',
)


class MainState(StatesGroup):
    STATE_FUNCTION = None
    customer = State()
    manager = State()
