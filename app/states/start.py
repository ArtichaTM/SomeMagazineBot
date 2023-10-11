# Libraries imports
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import InlineKeyboardMarkup

# App imports
from db import find_by_id, create_customer
from extra.functions import delete_msg
from .states import MainState


__all__ = ('router', )


router = Router()


@router.message(CommandStart())
async def command_start_handler(message: Message | CallbackQuery, state: FSMContext) -> None:
    """
    This handler receives messages with `/start` command
    """
    data = await state.get_data()
    user_id = message.from_user.id
    if isinstance(message, Message):
        chat_id = message.chat.id
        await delete_msg(message, 0.5)
    else:
        chat_id = message.message.chat.id
    someone = find_by_id(user_id)
    kb = []
    if someone.customer is None and someone.manager is None:
        someone = create_customer(user_id)
        name = message.from_user.first_name
        await message.answer(f"Добро пожаловать в магазин, {hbold(name)}!") 
    if someone.customer is not None:
        kb.extend([
            MainState._BUTTONS[MainState.S.products],
            MainState._BUTTONS[MainState.S.orders],
            MainState._BUTTONS[MainState.S.ordershistory]
        ])
    if someone.manager is not None:
        kb.append(MainState._BUTTONS[MainState.S.analytics])
    title = 'Главное меню'
    if 'messages' not in data:
        message = await message.answer(
            title,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[kb])
        )
        data['messages'] = [message.message_id]
    else:
        for sent_message in data['messages'][1:]:
            sent_message: int
            await message.bot.delete_message(message.chat.id, sent_message)
        data['messages'] = data['messages'][:1]
        await message.bot.edit_message_text(
            chat_id=chat_id,
            message_id=data['messages'][-1],
            text=title,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[kb])
        )
    data.update({'customer': someone.customer, 'manager': someone.manager})
    await state.set_data(data)


MainState._STATE_FUNCTION = command_start_handler
