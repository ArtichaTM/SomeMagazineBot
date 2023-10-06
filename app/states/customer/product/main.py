from io import StringIO
from collections import namedtuple
from typing import Sequence

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from sqlalchemy import TextClause, insert, select, Select, text, update
from sqlalchemy.orm import Session

from db import OrderHistory, OrderStatus, Product, Customer, Order, SQL_SCHEMA
from settings import Settings
from .states import CustomerProductView

router = Router()


def _menu(has_in_cart: bool) -> ReplyKeyboardMarkup:
    kb = [KeyboardButton(text='Назад'), KeyboardButton(text='Описание')]
    if has_in_cart:
        kb.append(KeyboardButton(text='Убрать из корзины'))
        kb.append(KeyboardButton(text='Добавить ещё в корзину'))
    else:
        kb.append(KeyboardButton(text='Добавить в корзину'))
    return ReplyKeyboardMarkup(keyboard=[kb], resize_keyboard=True)


async def start(message: Message, state: FSMContext) -> None:
    await state.set_state(CustomerProductView.main)
    data = await state.get_data()
    product: Product = data['product']
    user: Customer = data['customer']
    output = StringIO()
    output.write(f'Выбран продукт {product.name}')

    ordercurrent_sum: TextClause = text(f"""
        SELECT SUM(op.amount)
        FROM {SQL_SCHEMA}.OrderProduct as op
        INNER JOIN {SQL_SCHEMA}.`Order` as o ON (op.order_id = o.id)
        WHERE op.product_id = {product.id} AND o.customer_id = {user.id};
    """)
    ordershistory_sum: TextClause = text(f"""
        SELECT SUM(ohp.amount)
        FROM {SQL_SCHEMA}.OrderHistoryProduct as ohp
        INNER JOIN {SQL_SCHEMA}.`OrderHistory` as oh ON (ohp.order_id = oh.id)
        WHERE ohp.product_id = {product.id} AND oh.customer_id = {user.id};
    """)
    with Session(Settings['sql_engine']) as sess:
        ordercurrent_sum: int = sess.execute(ordercurrent_sum).scalar()
        ordercurrent_sum: int = 0 if ordercurrent_sum is None else ordercurrent_sum
        ordershistory_sum: int = sess.execute(ordershistory_sum).scalar()
        ordershistory_sum: int = 0 if ordershistory_sum is None else ordershistory_sum
        cart = user.get_cart(sess)

        product_in_cart = False
        for cart_product in cart:
            if cart_product.product_id == product.id:
                product_in_cart = True
                break

        if product_in_cart:
            ordercurrent_sum -= 1
            output.write('\n• Товар находится в вашей корзине')
            keyboard = _menu(True)
        else:
            keyboard = _menu(False)

        if product.amount == 0:
            output.write('\n• Товар в данный момент отсутствует')
        else:
            output.write('\n• Товар в наличии')

        if ordershistory_sum:
            output.write('\n• Вы уже заказывали этот товар')

        if ordercurrent_sum:
            output.write('\n• Ваш заказ на этот товар в процессе')

    await message.answer(output.getvalue(), reply_markup=keyboard)
    await state.set_data(data)


@router.message(CustomerProductView.main, F.text == 'Назад')
async def back(message: Message, state: FSMContext) -> None:
    await CustomerProductView.parent.STATE_FUNCTION(message, state)


@router.message(CustomerProductView.main, F.text == 'Описание')
async def back(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    product: Product = data['product']
    await message.answer(product.description)


@router.message(CustomerProductView.main, F.text == 'Убрать из корзины')
async def cart_remove(message: Message, state: FSMContext) -> None:
    data: dict = await state.get_data()
    user: Customer = data['customer']
    product: Product = data['product']

    with Session(Settings['sql_engine']) as sess:
        cart = user.get_cart(sess)
        for cart_value in cart:
            if cart_value.product_id == product.id:
                break
        else:
            await message.answer('Данного товара в корзине нет')
            return
        if cart_value.product_in_cart_amount == 1:
            stmt: TextClause = text(f"""
                DELETE FROM {SQL_SCHEMA}.OrderProduct
                WHERE
                    OrderProduct.order_id = {cart_value.order_id}
                    AND
                    OrderProduct.product_id = {cart_value.product_id}
            """)
            await message.answer(f'Последний товар убран из корзины', reply_markup=_menu(False))
        else:
            stmt: TextClause = text(f"""
                UPDATE {SQL_SCHEMA}.OrderProduct as op
                SET op.amount = {cart_value.product_in_cart_amount-1}
                WHERE
                    op.order_id = {cart_value.order_id}
                    AND
                    op.product_id = {cart_value.product_id}
            """)
            await message.answer(f'Один товар убран из корзины. Осталось: {cart_value.product_in_cart_amount-1}')
        sess.execute(stmt)
        sess.commit()


@router.message(CustomerProductView.main, F.text.in_({'Добавить в корзину', 'Добавить ещё в корзину'}))
async def cart_add(message: Message, state: FSMContext) -> None:
    data: dict = await state.get_data()
    user: Customer = data['customer']
    product: Product = data['product']

    amount: int = 0
    answer = {
        'text': "Товар успешно добавлен в корзину"
    }
    with Session(Settings['sql_engine']) as sess:
        cart = user.get_cart(sess)
        for cart_value in cart:
            if cart_value.product_id == product.id:
                answer['text'] += f'\nКоличество товара в корзине: {cart_value.product_in_cart_amount+1}'
                stmt: TextClause = text(f"""
                    UPDATE {SQL_SCHEMA}.OrderProduct as op
                    SET op.amount = {cart_value.product_in_cart_amount+1}
                    WHERE
                        op.order_id = {cart_value.order_id}
                        AND
                        op.product_id = {cart_value.product_id}
                """)
                break
        else:
            answer['reply_markup'] = _menu(True)
            stmt: TextClause = text(f"""
                INSERT INTO {SQL_SCHEMA}.OrderProduct (order_id, product_id, amount)
                VALUES ({cart_value.order_id}, {product.id}, 1)
            """)
        sess.execute(stmt)
        sess.commit()

        await message.answer(**answer)

CustomerProductView.STATE_FUNCTION = start
