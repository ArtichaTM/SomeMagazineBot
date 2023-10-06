from aiogram.fsm.state import State, StatesGroup

from ..states import ProductsList


class CustomerProductView(StatesGroup):
    parent = ProductsList
    STATE_FUNCTION = None
    main = State()
