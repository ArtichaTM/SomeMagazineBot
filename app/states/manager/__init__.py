from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import Router

from db import Customer, Manager


router = Router()


async def build_menu(state: FSMContext) -> ReplyKeyboardMarkup:
    # user: Customer | Manager = (await state.get_data())['user']
    return ReplyKeyboardMarkup(
        keyboard=[[
                KeyboardButton(text='Аналитика')
        ]],
        resize_keyboard=True
    )
