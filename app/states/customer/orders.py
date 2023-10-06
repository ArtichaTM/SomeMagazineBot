from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db import Product
from ..states import MainState


router = Router()


@router.message(MainState.customer, F.text == 'История заказов')
async def orders(message: Message, state: FSMContext) -> None:
    pass
