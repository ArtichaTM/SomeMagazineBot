from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from .states import ProductsDecision, ProductsList, ProductsNamePrompt
from ..states import MainState


__all__ = ('router', )


router = Router()


@router.message(MainState.main, F.text == 'Просмотреть товары')
async def decision(message: Message, state: FSMContext) -> None:
    await message.answer('Воспользуетесь поиском?', reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Назад'), KeyboardButton(text='Да'), KeyboardButton(text='Нет')]],
        resize_keyboard=True
    ))
    await state.set_state(ProductsDecision.main)


@router.message(ProductsDecision.main, F.text == 'Нет')
async def no(message: Message, state: FSMContext) -> None:
    await ProductsList.STATE_FUNCTION(message, state)
    await state.set_state(ProductsList.main)


@router.message(ProductsDecision.main, F.text == 'Да')
async def yes(message: Message, state: FSMContext) -> None:
    await message.answer(
        'Введите какую-либо часть названия товара',
        reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Назад')]])
    )
    await state.set_state(ProductsNamePrompt.main)


@router.message(ProductsDecision.main, F.text == 'Назад')
async def back(message: Message, state: FSMContext) -> None:
    await ProductsDecision.parent.STATE_FUNCTION(message, state)


@router.message(ProductsNamePrompt.main, F.text == 'Назад')
async def name_prompt_back(message: Message, state: FSMContext) -> None:
    await ProductsNamePrompt.parent.STATE_FUNCTION(message, state)


@router.message(ProductsNamePrompt.main)
async def name_prompt(message: Message, state: FSMContext) -> None:
    await state.update_data({'query': message.text})
    await ProductsList.STATE_FUNCTION(message, state)


ProductsDecision.STATE_FUNCTION = decision
ProductsNamePrompt.STATE_FUNCTION = yes
