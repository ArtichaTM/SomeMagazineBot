from io import StringIO

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy.orm import Session

from db import ORDER_PRODUCT, Order, OrderStatus, Product
from settings import Settings
from .states import OrderView
from .list import NAMES


router = Router()


@router.callback_query(OrderView.filter(F.function == OrderView.S.cart_buy))
async def cart_buy(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer('No, you are not')
