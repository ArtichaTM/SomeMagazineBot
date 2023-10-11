from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from ..states import MainState
from .order.states import OrderList
from .orderhistory.states import OrderHistoryList


router = Router()


@router.callback_query(MainState.filter(F.function == MainState.S.orders))
async def orders(message: Message, state: FSMContext) -> None:
    await OrderList._STATE_FUNCTION(message, state)


@router.callback_query(MainState.filter(F.function == MainState.S.ordershistory))
async def ordershistory(message: Message, state: FSMContext) -> None:
    await OrderHistoryList._STATE_FUNCTION(message, state)
