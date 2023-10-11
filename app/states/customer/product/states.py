from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton

from ..states import ProductsList


class CustomerProductView(CallbackData, prefix='CuPrVi'):
    class S(IntEnum):
        back = auto()
        add_cart = auto()
        add_another_cart = auto()
        remove_cart = auto()

    _parent = ProductsList
    _STATE_FUNCTION = None
    function: S


CustomerProductView._BUTTONS = {
    CustomerProductView.S.back: InlineKeyboardButton(
        text='Назад',
        callback_data=CustomerProductView(function=CustomerProductView.S.back).pack()
    ),
    CustomerProductView.S.add_cart: InlineKeyboardButton(
        text='Добавить в корзину',
        callback_data=CustomerProductView(function=CustomerProductView.S.add_cart).pack()
    ),
    CustomerProductView.S.add_another_cart: InlineKeyboardButton(
        text='Добавить ещё в корзину',
        callback_data=CustomerProductView(function=CustomerProductView.S.add_another_cart).pack()
    ),
    CustomerProductView.S.remove_cart: InlineKeyboardButton(
        text='Убрать из корзины',
        callback_data=CustomerProductView(function=CustomerProductView.S.remove_cart).pack()
    ),
}
