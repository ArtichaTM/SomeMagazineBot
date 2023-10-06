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
    bot: Bot = Settings['bot']
    user_id = message.from_user.id
    someone = find_by_id(user_id)
    if isinstance(someone, Customer):
        await state.set_state(MainState.customer)
        kb = await customer_menu(MainState.customer)
    elif isinstance(someone, Manager):
        await state.set_state(MainState.manager)
        kb = await manager_menu(MainState.manager)
    elif someone is None:
        someone = create_customer(user_id)
        name = message.from_user.first_name
        await state.set_state(MainState.customer)
        kb = await customer_menu(MainState.customer)
        await bot.send_message(message.chat.id, f"Добро пожаловать в магазин, {hbold(name)}!")
    else:
        raise RuntimeError("Unknown return type from \"find_by_id\".")
    await state.set_data({'user': someone})

    await message.answer('Главное меню', reply_markup=kb)


MainState.STATE_FUNCTION = command_start_handler
