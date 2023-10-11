from functools import partial

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from sqlalchemy import Select
from sqlalchemy.orm import Session

from db import Customer, Product
from extra.functions import delete_msg
from settings import Settings
from .states import ProductNamePrompt, ProductsDecision, ProductsList, ProductsNamePrompt
from ..states import MainState

__all__ = ('router',)

router = Router()


@router.callback_query(MainState.filter(F.function == MainState.S.products))
async def decision(query: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await query.bot.edit_message_text(
        chat_id=query.message.chat.id,
        message_id=data['messages'][-1],
        text='Воспользуетесь поиском?',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                ProductsDecision._BUTTONS[ProductsDecision.S.back],
                ProductsDecision._BUTTONS[ProductsDecision.S.search],
                ProductsDecision._BUTTONS[ProductsDecision.S.all_products],
                ProductsDecision._BUTTONS[ProductsDecision.S.cart_products],
            ]],
        ))


@router.callback_query(ProductsDecision.filter(F.function == ProductsDecision.S.all_products))
async def all_products(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data({'products_query': None})
    await ProductsList._STATE_FUNCTION(callback, state)


@router.callback_query(ProductsDecision.filter(F.function ==ProductsDecision.S.search))
async def search(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=data['messages'][-1],
        text='Напишите какую-либо часть названия товара',
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[
                ProductsDecision._BUTTONS[ProductsDecision.S.back]
            ]]
        )
    )
    await state.set_state(ProductNamePrompt.main)


def _cart_products_select(stmt: Select, products_ids: list[int]) -> Select:
    return stmt.where(Product.id.in_(products_ids))


@router.callback_query(ProductsDecision.filter(F.function == ProductsDecision.S.cart_products))
async def cart_products(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    customer: Customer = data['customer']
    with Session(Settings['sql_engine']) as sess:
        cart = customer.get_cart(sess)
    products_ids = [product for product in cart]
    await state.update_data({'products_query': partial(_cart_products_select, products_ids=products_ids)})
    await ProductsList._STATE_FUNCTION(callback, state)


@router.callback_query(ProductsDecision.filter(F.function == ProductsDecision.S.back))
async def back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(None)
    await ProductsDecision._parent.default._STATE_FUNCTION(callback, state)


@router.callback_query(ProductsNamePrompt.filter(F.function == ProductsNamePrompt.S.back))
async def back(callback: CallbackQuery, state: FSMContext) -> None:
    await ProductsNamePrompt._parent.default._STATE_FUNCTION(callback, state)


@router.message(ProductNamePrompt.main)
async def name_prompt(message: Message, state: FSMContext) -> None:
    await state.update_data({'products_query': message.text})
    await delete_msg(message, 0.5)
    await ProductsList._STATE_FUNCTION(message, state)


ProductsDecision._STATE_FUNCTION = decision
ProductsNamePrompt._STATE_FUNCTION = search
