from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import Router

from .products import router as products_router
from .products_list import router as products_list_router
from .orders import router as orders_router
from .product import router as product_router

__all__ = (
    'router',
    'build_menu'
)


router = Router()
router.include_routers(
    products_router,
    products_list_router,
    orders_router,
    product_router
)


async def build_menu(state: FSMContext) -> list[KeyboardButton]:
    return [
        KeyboardButton(text='Просмотреть товары'),
        KeyboardButton(text='История заказов')
    ]
