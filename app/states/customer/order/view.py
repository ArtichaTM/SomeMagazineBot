from io import StringIO

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from sqlalchemy.orm import Session

from db import ORDER_PRODUCT, Order, OrderStatus, Product
from settings import Settings
from .states import OrderView
from .list import NAMES


router = Router()


async def _send_menu(callback: Message | CallbackQuery, state: FSMContext) -> None:
    chat_id = callback.chat.id if isinstance(callback, Message) else callback.message.chat.id
    data = await state.get_data()
    order: Order = data['order']
    kb = [OrderView._BUTTONS[OrderView.S.back]]
    with Session(Settings['sql_engine']) as sess:
        products = await order.products(sess)
    output = StringIO()

    overall_cost = 0
    overall_amount = 0
    if None in products:
        output.write('Корзина пуста')
    else:
        output.write(f'{NAMES[order.status]} c '
                     f'{sum(product.product_in_cart_amount for product in products.values())}'
                     f' товарами:')
        for index, product in enumerate(products.values(), start=1):
            product: ORDER_PRODUCT
            product_cost = await Product.current_cost(sess, product.product_id, product.product_cost)
            overall_amount += product.product_in_cart_amount
            overall_cost += product_cost*product.product_in_cart_amount
            output.write(f"\n{index}. "
                         f"{product.product_name}: "
                         f"{product_cost}₽ x {product.product_in_cart_amount}")

        output.write(f'\n\nТип заказа: {NAMES[order.status].lower()}')
        output.write(f'\nКоличество наименований: {overall_amount}')
        output.write(f'\nИтоговая цена на момент сообщения: {overall_cost}₽')

    if order.status == OrderStatus.CART and overall_amount > 0:
        kb.append(OrderView._BUTTONS[OrderView.S.cart_buy])

    await callback.bot.edit_message_text(
        chat_id=chat_id,
        message_id=data['messages'][-1],
        text=output.getvalue(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[kb])
    )


async def start(callback: Message | CallbackQuery, state: FSMContext) -> None:
    await _send_menu(callback, state)


@router.callback_query(OrderView.filter(F.function == OrderView.S.back))
async def back(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(None)
    await OrderView._parent.default._STATE_FUNCTION(callback, state)


OrderView._STATE_FUNCTION = start
