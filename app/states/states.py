from enum import IntEnum, auto

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton


__all__ = (
    'MainState',
)


class MainState(CallbackData, prefix='main'):
    class S(IntEnum):
        products = auto()
        orders = auto()
        ordershistory = auto()
        analytics = auto()

    _BUTTONS = dict()
    _STATE_FUNCTION = None
    function: S


MainState._BUTTONS = {
    MainState.S.products: InlineKeyboardButton(
        text='Просмотреть товары',
        callback_data=MainState(function=MainState.S.products).pack()
    ),
    MainState.S.orders: InlineKeyboardButton(
        text='Текущие заказы',
        callback_data=MainState(function=MainState.S.orders).pack()
    ),
    MainState.S.ordershistory: InlineKeyboardButton(
        text='История заказов',
        callback_data=MainState(function=MainState.S.ordershistory).pack()
    ),
    MainState.S.analytics: InlineKeyboardButton(
        text='Аналитика',
        callback_data=MainState(function=MainState.S.analytics).pack()
    )

}
