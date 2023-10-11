from io import StringIO

from aiogram import Router, F
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy import TextClause, text
from sqlalchemy.orm import Session

from db import Product, Customer, SQL_SCHEMA
from settings import Settings
from .states import CustomerProductView

router = Router()


def _menu(has_in_cart: bool) -> InlineKeyboardMarkup:
    kb = [
        CustomerProductView._BUTTONS[CustomerProductView.S.back]
    ]
    if has_in_cart:
        kb.append(CustomerProductView._BUTTONS[CustomerProductView.S.remove_cart])
        kb.append(CustomerProductView._BUTTONS[CustomerProductView.S.add_another_cart])
    else:
        kb.append(CustomerProductView._BUTTONS[CustomerProductView.S.add_cart])
    return InlineKeyboardMarkup(inline_keyboard=[kb])


async def _send_description(
        callback: Message | CallbackQuery,
        state: FSMContext
) -> None:
    data = await state.get_data()
    product: Product = data['product']
    user: Customer = data['customer']
    output = StringIO()
    output.write(f'Выбран продукт {product.name}')

    ordercurrent_sum: TextClause = text(f"""
        SELECT COUNT(*)
        FROM {SQL_SCHEMA}.OrderProduct as op
        INNER JOIN {SQL_SCHEMA}.`Order` as o ON (op.order_id = o.id)
        WHERE op.product_id = {product.id} AND o.customer_id = {user.id};
    """)
    ordershistory_sum: TextClause = text(f"""
        SELECT COUNT(*)
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
        ORDER_PRODUCT = cart.get(product.id, None)

        if ORDER_PRODUCT is not None:
            ordercurrent_sum -= 1
            product_in_cart = ORDER_PRODUCT.product_in_cart_amount
            if product_in_cart == 1:
                output.write('\n• Товар находится в вашей корзине')
            else:
                output.write(f'\n• {product_in_cart} товара(-ов) находится в вашей корзине')
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

    if isinstance(callback, Message):
        chat_id = callback.chat.id
    else:
        chat_id = callback.message.chat.id

    await state.set_data(data)
    await callback.bot.edit_message_text(
        chat_id=chat_id,
        message_id=data['messages'][-1],
        text=output.getvalue(),
        reply_markup=keyboard
    )


async def start(callback: CallbackData | Message, state: FSMContext) -> None:
    await _send_description(callback, state)


@router.callback_query(CustomerProductView.filter(F.function == CustomerProductView.S.back))
async def back(callback: CallbackQuery, state: FSMContext) -> None:
    await CustomerProductView._parent.default._STATE_FUNCTION(callback, state)


@router.callback_query(CustomerProductView.filter(F.function == CustomerProductView.S.remove_cart))
async def cart_remove(callback: CallbackQuery, state: FSMContext) -> None:
    data: dict = await state.get_data()
    user: Customer = data['customer']
    product: Product = data['product']

    with Session(Settings['sql_engine']) as sess:
        cart = user.get_cart(sess)
        ORDER_PRODUCT = cart.get(product.id, None)

        if ORDER_PRODUCT is None:
            return
        if ORDER_PRODUCT.product_in_cart_amount == 1:
            stmt: TextClause = text(f"""
                DELETE FROM {SQL_SCHEMA}.OrderProduct
                WHERE
                    OrderProduct.order_id = {ORDER_PRODUCT.order_id}
                    AND
                    OrderProduct.product_id = {ORDER_PRODUCT.product_id}
            """)
        else:
            stmt: TextClause = text(f"""
                UPDATE {SQL_SCHEMA}.OrderProduct as op
                SET op.amount = {ORDER_PRODUCT.product_in_cart_amount-1}
                WHERE
                    op.order_id = {ORDER_PRODUCT.order_id}
                    AND
                    op.product_id = {ORDER_PRODUCT.product_id}
            """)
        sess.execute(stmt)
        sess.commit()
    await _send_description(callback, state)


@router.callback_query(CustomerProductView.filter(F.function.in_({
    CustomerProductView.S.add_cart,
    CustomerProductView.S.add_another_cart
})))
async def cart_add(callback: CallbackQuery, state: FSMContext) -> None:
    data: dict = await state.get_data()
    user: Customer = data['customer']
    product: Product = data['product']

    with Session(Settings['sql_engine']) as sess:
        cart = user.get_cart(sess)
        ORDER_PRODUCT = cart.get(product.id, None)

        if ORDER_PRODUCT is not None:
            stmt: TextClause = text(f"""
                UPDATE {SQL_SCHEMA}.OrderProduct as op
                SET op.amount = {ORDER_PRODUCT.product_in_cart_amount+1}
                WHERE
                    op.order_id = {ORDER_PRODUCT.order_id}
                    AND
                    op.product_id = {ORDER_PRODUCT.product_id}
            """)
        else:
            stmt: TextClause = text(f"""
                INSERT INTO {SQL_SCHEMA}.OrderProduct (order_id, product_id, amount)
                VALUES ({next(iter(cart.values())).order_id}, {product.id}, 1)
            """)
        sess.execute(stmt)
        sess.commit()
        await _send_description(callback, state)


CustomerProductView._STATE_FUNCTION = start
