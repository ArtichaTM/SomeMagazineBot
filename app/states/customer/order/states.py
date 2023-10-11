from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton

from ..states import MainState


class OrderList(CallbackData, prefix='orli'):
    class S(IntEnum):
        back = auto()
        next = auto()
        previous = auto()

    _parent = MainState
    _STATE_FUNCTION = None
    function: S


OrderList._BUTTONS = {
    OrderList.S.back: InlineKeyboardButton(
        text='Назад',
        callback_data=OrderList(function=OrderList.S.back).pack()
    ),
    OrderList.S.next: InlineKeyboardButton(
        text='Cледующая',
        callback_data=OrderList(function=OrderList.S.next).pack()
    ),
    OrderList.S.previous: InlineKeyboardButton(
        text='Предыдущая',
        callback_data=OrderList(function=OrderList.S.previous).pack()
    ),
}


class OrderListPrompt(StatesGroup):
    main = State()


class OrderView(CallbackData, prefix='orvi'):
    class S(IntEnum):
        back = auto()
        cart_buy = auto()

    _parent = OrderList
    _STATE_FUNCTION = None
    function: S


OrderView._BUTTONS = {
    OrderView.S.back: InlineKeyboardButton(
        text='Назад',
        callback_data=OrderView(function=OrderView.S.back).pack()
    ),
    OrderView.S.cart_buy: InlineKeyboardButton(
        text='Оформить заказ',
        callback_data=OrderView(function=OrderView.S.cart_buy).pack()
    ),
}

