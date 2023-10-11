import asyncio
from io import StringIO

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.markdown import hbold
from sqlalchemy import select
from sqlalchemy.orm import Session

from settings import Settings
from db import Customer, Order, OrderStatus
from extra.functions import delete_msg
from .states import OrderList, OrderListPrompt, OrderView

router = Router()


NAMES = {
    OrderStatus.CART: 'Корзина',
    OrderStatus.PAYING: 'Ожидающий оплату заказ',
    OrderStatus.WAITING_FOR_TAKE: 'Ожидающий выдачу заказ'
}


async def _send_menu(callback: CallbackQuery | Message, state: FSMContext) -> None:
    chat_id = callback.chat.id if isinstance(callback, Message) else callback.message.chat.id
    data = await state.get_data()
    customer: Customer = data['customer']
    limit = Settings.get('orders_limit', 9)
    offset = data['order_list_offset']
    kb = [
        OrderList._BUTTONS[OrderList.S.back],
    ]

    orders = await Order.list(customer.id, offset, limit+1)
    if offset != 0:
        kb.append(OrderList._BUTTONS[OrderList.S.previous])
    if len(orders) > limit:
        kb.append(OrderList._BUTTONS[OrderList.S.next])
    orders = orders[:limit]

    output = StringIO()
    output.write('Для просмотра какого-либо заказа, введите его цифру\n\n')
    output.write(f'> Страница {offset // limit + 1}')
    for or_id, order in enumerate(orders, start=1):
        order: Order
        or_id = hbold(f"{or_id}.")
        amount = await order.products_overall_amount()
        if amount == 0:
            output.write(f"\n{or_id} {NAMES[order.status]} без товаров")
        else:
            output.write(f"\n{or_id} {NAMES[order.status]} c {amount} товарами")
    await callback.bot.edit_message_text(
        chat_id=chat_id,
        message_id=data['messages'][-1],
        text=output.getvalue(),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[kb])
    )


async def start(callback: CallbackQuery, state: FSMContext) -> None:
    # data = await state.get_data()
    # limit = Settings.get('orders_limit', 9)
    # await state.update_data({'orders_offset': 0})
    # output = StringIO()
    # output.write('Для просмотра какого-либо заказа, введите его цифру\n\n')
    # output.write(f'> Страница 1')
    # orders = await Order.list(callback.from_user.id, 0, limit)
    # 
    # for pr_id, order in enumerate(orders, start=1):
    #     order: Order
    #     products_overall_amount = await order.products_overall_amount()
    #     pr_id = hbold(f"{pr_id}.")
    #     products_text = {
    #         0: 'без товаров',
    #         1: f'c {products_overall_amount} товаром'
    #     }.get(products_overall_amount, f'c {products_overall_amount} товарами')
    #     output.write({
    #         OrderStatus.CART: f"\n{pr_id} Корзина ",
    #         OrderStatus.PAYING: f"\n{pr_id} Ожидающий оплату заказ ",
    #         OrderStatus.WAITING_FOR_TAKE: f"\n{pr_id} Ожидающий выдачи заказ "
    #     }[order.status])
    #     output.write(products_text)
    #
    # orders_count = await Order.amount(callback.from_user.id)
    # kb = [KeyboardButton(text='Назад')]
    # if orders_count > limit:
    #     kb.append(InlineKeyboardButton(text='Следующая'))
    # await callback.bot.edit_message_text(
    #     chat_id=callback.message.chat.id,
    #     message_id=data['messages'][-1],
    #     text=output.getvalue(),
    #     reply_markup=InlineKeyboardMarkup(
    #         inline_keyboard=[kb]
    #     )
    # )
    await state.set_state(OrderListPrompt.main)
    await state.update_data({'order_list_offset': 0})
    await _send_menu(callback, state)


@router.callback_query(OrderList.filter(F.function == OrderList.S.next))
async def go_next(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    limit = Settings.get('orders_limit', 9)
    await state.update_data({'order_list_offset': data['order_list_offset'] + limit})
    await _send_menu(callback, state)


@router.callback_query(OrderList.filter(F.function == OrderList.S.previous))
async def go_previous(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    limit = Settings.get('orders_limit', 9)
    await state.update_data({'order_list_offset': data['order_list_offset'] - limit})
    await _send_menu(callback, state)


@router.callback_query(OrderList.filter(F.function == OrderList.S.back))
async def back(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(None)
    data.pop('order_list_offset')
    await OrderList._parent.default._STATE_FUNCTION(callback, state)


@router.message(OrderListPrompt.main, F.text.regexp(r'\d'))
async def item_id(message: Message, state: FSMContext) -> None:
    # data = await state.get_data()
    # if len(message.text) > 1:
    #     await message.answer('Введено больше одного символа')
    #     return
    # 
    # index = int(message.text[0])
    # if index == 0:
    #     await message.answer('Номера 0 в списке нет')
    #     return
    # 
    # 
    # if order is None:
    #     await message.answer(f'Номера {index} в списке нет')
    #     return
    # data['order'] = order
    # await state.set_data(data)
    # await OrderView._STATE_FUNCTION(message, state)
    await delete_msg(message, 0.5)
    data = await state.get_data()
    customer: Customer = data['customer']
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

    order = select(Order) \
        .where(Order.customer_id == customer.id) \
        .offset(data['order_list_offset'] + index - 1)
    with Session(Settings['sql_engine']) as sess:
        order = sess.execute(order).scalar()

    if order is None:
        sent_message = await message.answer(f'Номера {index} в списке нет')
        await delete_msg(sent_message, 2)
        return
    data['order'] = order
    await state.set_data(data)
    await state.set_state(None)
    await OrderView._STATE_FUNCTION(message, state)


OrderList._STATE_FUNCTION = start
