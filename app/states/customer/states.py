from enum import IntEnum, auto

from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton

from ..states import MainState


class ProductsDecision(CallbackData, prefix='prde'):
    class S(IntEnum):
        back = auto()
        search = auto()
        all_products = auto()
        cart_products = auto()

    _parent = MainState
    _STATE_FUNCTION = None
    _BUTTONS: dict
    function: S


ProductsDecision._BUTTONS = {
    ProductsDecision.S.back: InlineKeyboardButton(
        text='Назад',
        callback_data=ProductsDecision(function=ProductsDecision.S.back).pack()
    ),
    ProductsDecision.S.search: InlineKeyboardButton(
        text='Поиск',
        callback_data=ProductsDecision(function=ProductsDecision.S.search).pack()
    ),
    ProductsDecision.S.all_products: InlineKeyboardButton(
        text='Все продукты',
        callback_data=ProductsDecision(function=ProductsDecision.S.all_products).pack()
    ),
    ProductsDecision.S.cart_products: InlineKeyboardButton(
        text='Товары в корзине',
        callback_data=ProductsDecision(function=ProductsDecision.S.cart_products).pack()
    ),
}


class ProductsNamePrompt(CallbackData, prefix='prnapr'):
    class S(IntEnum):
        back = auto()
        yes = auto()
        no = auto()

    _parent = MainState
    _STATE_FUNCTION = None
    _BUTTONS: dict
    function: S


ProductsNamePrompt._BUTTONS = {
    ProductsNamePrompt.S.back: InlineKeyboardButton(
        text='Назад',
        callback_data=ProductsNamePrompt(function=ProductsNamePrompt.S.back).pack()
    ),
    ProductsNamePrompt.S.yes: InlineKeyboardButton(
        text='Да',
        callback_data=ProductsNamePrompt(function=ProductsNamePrompt.S.yes).pack()
    ),
    ProductsNamePrompt.S.no: InlineKeyboardButton(
        text='Нет',
        callback_data=ProductsNamePrompt(function=ProductsNamePrompt.S.no).pack()
    ),
}


class ProductNamePrompt(StatesGroup):
    main = State()


class ProductsListPrompt(StatesGroup):
    main = State()


class ProductsList(CallbackData, prefix='prli'):
    class S(IntEnum):
        back = auto()
        next = auto()
        previous = auto()

    _parent = MainState
    _STATE_FUNCTION = None
    function: S


ProductsList._BUTTONS = {
    ProductsList.S.back: InlineKeyboardButton(
        text='Назад',
        callback_data=ProductsList(function=ProductsList.S.back).pack()
    ),
    ProductsList.S.next: InlineKeyboardButton(
        text='Cледующая',
        callback_data=ProductsList(function=ProductsList.S.next).pack()
    ),
    ProductsList.S.previous: InlineKeyboardButton(
        text='Предыдущая',
        callback_data=ProductsList(function=ProductsList.S.previous).pack()
    ),
}
