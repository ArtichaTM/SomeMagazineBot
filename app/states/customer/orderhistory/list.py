from io import StringIO

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Message, \
    ReplyKeyboardMarkup
from aiogram.utils.markdown import hbold

from db import OrderHistory
from settings import Settings
from .states import OrderHistoryList


router = Router()


async def start(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(OrderHistoryList.main)
    data = await state.get_data()
    limit = Settings.get('orders_limit', 9)
    await state.update_data({'ordershistory_offset': 0})
    output = StringIO()
    output.write('Для просмотра какого-либо заказа, введите его цифру\n\n')
    output.write(f'> Страница 1')
    ordershistory = await OrderHistory.list(callback.from_user.id, 0, limit)

    for pr_id, orderhistory in enumerate(ordershistory, start=1):
        orderhistory: OrderHistory
        pr_id = hbold(f"{pr_id}.")
        output.write(f"\n{pr_id} Заказ от {orderhistory.date_completed:%d:%m:%Y}")

    await callback.bot.edit_message_text(
        chat_id=callback.message.chat.id,
        message_id=data['messages'][-1],
        text=output.getvalue(),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text='Назад'), InlineKeyboardButton(text='Следующая')]]
    ))


# @router.message(ProductsList.main, F.text == 'Следующая')
# async def go_next(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     limit = Settings.get('products_limit', 10)
#     offset = data['ordershistory_offset'] + limit
#     await state.update_data({'ordershistory_offset': offset})
# 
#     products = await Product.list(offset, limit, data.get('query', None))
#     bot: Bot = Settings['bot']
#     output = LongMessage(message)
#     await output.write(f'> Страница {offset // limit + 1}')
#     for pr_id, product in enumerate(products, start=1):
#         product: Product
#         pr_id = hbold(f"{pr_id}.")
#         await output.write(f"\n{pr_id} {product.name}")
#     await bot.send_message(message.chat.id, text=output.getvalue(), reply_markup=ReplyKeyboardMarkup(
#         keyboard=[[
#             KeyboardButton(text='Назад'),
#             KeyboardButton(text='Предыдущая'),
#             KeyboardButton(text='Следующая')
#         ]],
#         resize_keyboard=True
#     ))


# @router.message(ProductsList.main, F.text == 'Предыдущая')
# async def go_previous(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     limit = Settings.get('products_limit', 10)
#     offset = data['ordershistory_offset'] - limit
#     await state.update_data({'ordershistory_offset': offset})
#     products = await Product.list(offset, limit, data.get('query', None))
#     bot: Bot = Settings['bot']
#     output = LongMessage(message)
#     await output.write(f'> Страница {offset // limit + 1}')
#     for pr_id, product in enumerate(products, start=1):
#         product: Product
#         pr_id = hbold(f"{pr_id}.")
#         await output.write(f"\n{pr_id} {product.name}")
#     buttons = [KeyboardButton(text='Назад')]
#     if offset != 0:
#         buttons.append(KeyboardButton(text='Предыдущая'))
#     buttons.append(KeyboardButton(text='Следующая'))
#     await bot.send_message(message.chat.id, text=output.getvalue(), reply_markup=ReplyKeyboardMarkup(
#         keyboard=[buttons],
#         resize_keyboard=True
#     ))


@router.message(OrderHistoryList.main, F.text == 'Назад')
async def back(message: Message, state: FSMContext) -> None:
    await OrderHistoryList._parent.default._STATE_FUNCTION(message, state)


# @router.message(ProductsList.main, F.text.regexp(r'\d'))
# async def item_id(message: Message, state: FSMContext) -> None:
#     data = await state.get_data()
#     if len(message.text) > 1:
#         await message.answer('Введено больше одного символа')
#         return
#
#     index = int(message.text[0])
#     if index == 0:
#         await message.answer('Номера 0 в списке нет')
#         return
# 
#     stmt = select(Product).offset(data['ordershistory_offset'] + index - 1)
#     if 'query' in data:
#         stmt = stmt.filter(Product.name.like(f"%{data['query']}%"))
#     with Session(Settings['sql_engine']) as sess:
#         print(stmt)
#         product = sess.execute(stmt).scalar()
# 
#     if product is None:
#         await message.answer(f'Номера {index} в списке нет')
#         return
#     data['product'] = product
#     await state.set_data(data)
#     await CustomerProductView._STATE_FUNCTION(message, state)


OrderHistoryList._STATE_FUNCTION = start
