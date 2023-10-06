from aiogram.fsm.state import State, StatesGroup

from ..states import MainState


class ProductsDecision(StatesGroup):
    parent = MainState
    STATE_FUNCTION = None
    main = State()


class ProductsNamePrompt(StatesGroup):
    parent = ProductsDecision
    STATE_FUNCTION = None
    main = State()


class ProductsList(StatesGroup):
    parent = ProductsDecision
    STATE_FUNCTION = None
    main = State()

