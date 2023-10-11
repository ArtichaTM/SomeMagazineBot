from aiogram.utils.keyboard import InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram import Router

# Files
from .products import router as products_router
from .products_list import router as products_list_router
from .orders import router as orders_router
# Folders
from .product import router as product_router
from .order import router as order_router
from .orderhistory import router as orderhistory_router

__all__ = (
    'router',
)


router = Router()
router.include_routers(
    products_router,
    products_list_router,
    orders_router,
    product_router,
    order_router,
    orderhistory_router
)
