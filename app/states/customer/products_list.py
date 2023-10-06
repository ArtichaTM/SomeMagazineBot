from aiogram import Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import select
from sqlalchemy.orm import Session

from db import Product
from functions import LongMessage
from settings import Settings
from .states import ProductsList, ProductsNamePrompt
from .product.states import CustomerProductView

router = Router()


async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(ProductsList.main)
    data = await state.get_data()
    limit = Settings.get('products_limit', 10)
    await state.update_data({'offset': 0})
    products = await Product.list(0, limit, data.get('query', None))
    output = LongMessage(message)
    bot: Bot = Settings['bot']
    await bot.send_message(message.chat.id, 'Для просмотра какого-либо товара, введите его цифру')
    await output.write(f'> Страница 1')
    for pr_id, product in enumerate(products, start=1):
        product: Product
        pr_id = hbold(f"{pr_id}.")
        await output.write(f"\n{pr_id} {product.name}")
    await bot.send_message(message.chat.id, text=output.getvalue(), reply_markup=ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text='Назад'), KeyboardButton(text='Следующая')]],
        resize_keyboard=True
    ))


@router.message(ProductsList.main, F.text == 'Следующая')
async def go_next(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    limit = Settings.get('products_limit', 10)
    offset = data['offset'] + limit
    await state.update_data({'offset': offset})

    products = await Product.list(offset, limit, data.get('query', None))
    bot: Bot = Settings['bot']
    output = LongMessage(message)
    await output.write(f'> Страница {offset // limit + 1}')
    for pr_id, product in enumerate(products, start=1):
        product: Product
        pr_id = hbold(f"{pr_id}.")
        await output.write(f"\n{pr_id} {product.name}")
    await bot.send_message(message.chat.id, text=output.getvalue(), reply_markup=ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text='Назад'),
            KeyboardButton(text='Предыдущая'),
            KeyboardButton(text='Следующая')
        ]],
        resize_keyboard=True
    ))


@router.message(ProductsList.main, F.text == 'Предыдущая')
async def go_previous(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    limit = Settings.get('products_limit', 10)
    offset = data['offset'] - limit
    await state.update_data({'offset': offset})
    products = await Product.list(offset, limit, data.get('query', None))
    bot: Bot = Settings['bot']
    output = LongMessage(message)
    await output.write(f'> Страница {offset // limit + 1}')
    for pr_id, product in enumerate(products, start=1):
        product: Product
        pr_id = hbold(f"{pr_id}.")
        await output.write(f"\n{pr_id} {product.name}")
    buttons = [KeyboardButton(text='Назад')]
    if offset != 0:
        buttons.append(KeyboardButton(text='Предыдущая'))
    buttons.append(KeyboardButton(text='Следующая'))
    await bot.send_message(message.chat.id, text=output.getvalue(), reply_markup=ReplyKeyboardMarkup(
        keyboard=[buttons],
        resize_keyboard=True
    ))


@router.message(ProductsList.main, F.text == 'Назад')
async def back(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    data.pop('offset')
    query = False
    if 'query' in data:
        query = True
        data.pop('query')
    await state.set_data(data)
    if query:
        await ProductsNamePrompt.STATE_FUNCTION(message, state)
    else:
        await ProductsList.parent.STATE_FUNCTION(message, state)


@router.message(ProductsList.main, F.text.regexp(r'\d'))
async def item_id(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if len(message.text) > 1:
        await message.answer('Введено больше одного символа')
        return

    index = int(message.text[0])
    if index == 0:
        await message.answer('Номера 0 в списке нет')
        return

    stmt = select(Product).offset(data['offset'] + index - 1)
    if 'query' in data:
        stmt = stmt.filter(Product.name.like(f"%{data['query']}%"))
    with Session(Settings['sql_engine']) as sess:
        print(stmt)
        product = sess.execute(stmt).scalar()

    if product is None:
        await message.answer(f'Номера {index} в списке нет')
        return
    data['product'] = product
    await state.set_data(data)
    await CustomerProductView.STATE_FUNCTION(message, state)


ProductsList.STATE_FUNCTION = start
