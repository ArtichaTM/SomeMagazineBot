from aiogram import Router

from .start import router as start_router
from .customer import router as customer_router
from .manager import router as manager_router


router = Router()
router.include_routers(
    customer_router,
    manager_router,
    start_router,
)
