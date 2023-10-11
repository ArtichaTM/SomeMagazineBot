import asyncio
import logging
from io import StringIO

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.markdown import hbold
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import Product
from settings import Settings
from extra.functions import delete_msg
from .states import ProductsList, ProductsListPrompt
from .product.states import CustomerProductView
router = Router()


async def _send_menu(
        callback: CallbackQuery | Message,
        state: FSMContext
) -> None:
    chat_id = callback.chat.id if isinstance(callback, Message) else callback.message.chat.id
    data = await state.get_data()
    limit = Settings.get('products_limit', 9)
    offset = data['products_list_offset']
    kb = [
        ProductsList._BUTTONS[ProductsList.S.back],
    ]

    products = await Product.list(offset, limit+1, data.get('products_query', None))
    if offset != 0:
        kb.append(ProductsList._BUTTONS[ProductsList.S.previous])
    if len(products) > limit:
        kb.append(ProductsList._BUTTONS[ProductsList.S.next])
    products = products[:limit]

    output = StringIO()
    output.write('Для просмотра какого-либо товара, введите его цифру\n\n')
    output.write(f'> Страница {offset // limit + 1}')
    for pr_id, product in enumerate(products, start=1):
        product: Product
        pr_id = hbold(f"{pr_id}.")
        output.write(f"\n{pr_id} {product.name}")
    await callback.bot.edit_message_text(
        chat_id=chat_id,
        message_id=data['messages'][-1],
        text=output.getvalue(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[kb])
    )


async def start(callback: CallbackQuery | Message, state: FSMContext) -> None:
    await state.set_state(ProductsListPrompt.main)
    await state.update_data({'products_list_offset': 0})
    await _send_menu(callback, state)


@router.callback_query(ProductsList.filter(F.function == ProductsList.S.next))
async def go_next(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    limit = Settings.get('products_limit', 9)
    await state.update_data({'products_list_offset': data['products_list_offset'] + limit})
    await _send_menu(callback, state)


@router.callback_query(ProductsList.filter(F.function == ProductsList.S.previous))
async def go_previous(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    limit = Settings.get('products_limit', 9)
    await state.update_data({'products_list_offset': data['products_list_offset'] - limit})
    await _send_menu(callback, state)


@router.callback_query(ProductsList.filter(F.function == ProductsList.S.back))
async def back(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(None)
    data.pop('products_list_offset')
    if 'products_query' in data:
        data.pop('products_query')
        await state.set_data(data)
    await ProductsList._parent.default._STATE_FUNCTION(callback, state)


@router.message(ProductsListPrompt.main)
async def item_id(message: Message, state: FSMContext) -> None:
    await delete_msg(message, 0.5)
    data = await state.get_data()
    if len(message.text) > 1:
        sent_message = await message.answer('Введено больше одного символа')
        await delete_msg(sent_message, 2)
        return
    elif len(message.text) == 0:
        sent_message = await message.answer('Отправлено сообщение с пустым текстом')
        await delete_msg(sent_message, 2)
        return
    elif message.text[0] not in {'1', '2', '3', '4', '5', '6', '7', '8', '9'}:
        sent_message = await message.answer('Отправлено не число')
        await delete_msg(sent_message, 2)
        return

    index = int(message.text[0])
    if index == 0:
        sent_message = await message.answer('Номера 0 в списке нет')
        await delete_msg(sent_message, 2)
        return

    stmt = select(Product).offset(data['products_list_offset'] + index - 1)
    query = data.get('products_query', None)
    if query is not None:
        if isinstance(query, str):
            stmt = stmt.filter(Product.name.like(f"%{data['products_query']}%"))
        elif callable(query):
            stmt = query(stmt)
        else:
            logging.error(f'What is this query? {query}, type {type(query)}')
    with Session(Settings['sql_engine']) as sess:
        product = sess.execute(stmt).scalar()

    if product is None:
        sent_message = await message.answer(f'Номера {index} в списке нет')
        await delete_msg(sent_message, 2)
        return
    data['product'] = product
    await state.set_data(data)
    await state.set_state(None)
    await CustomerProductView._STATE_FUNCTION(message, state)


ProductsList._STATE_FUNCTION = start
