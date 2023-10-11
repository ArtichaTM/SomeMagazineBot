from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .states import OrderHistoryView


router = Router()


async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(OrderHistoryView.main)


OrderHistoryView._STATE_FUNCTION = start
