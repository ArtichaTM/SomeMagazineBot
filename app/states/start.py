# Libraries imports
from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import ReplyKeyboardMarkup

# App imports
from db import Manager, Customer, find_by_id, create_customer
from settings import Settings
from .states import MainState
from .customer import build_menu as customer_menu
from .manager import build_menu as manager_menu


__all__ = ('router', )


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    user_id = message.from_user.id
    someone = find_by_id(user_id)
    kb = []
    if someone.customer is None and someone.manager is None:
        someone = (create_customer(user_id), None)
        name = message.from_user.first_name
        await message.answer(f"Добро пожаловать в магазин, {hbold(name)}!")
    if someone.customer is not None:
        kb.extend(await customer_menu(state))
    if someone.manager is not None:
        kb.extend(await manager_menu(state))
    await state.set_data({'customer': someone.customer, 'manager': someone.manager})
    await state.set_state(MainState.main)
    await message.answer('Главное меню', reply_markup=ReplyKeyboardMarkup(
        keyboard=[kb], resize_keyboard=True
    ))


MainState.STATE_FUNCTION = command_start_handler
