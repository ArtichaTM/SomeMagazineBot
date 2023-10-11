from aiogram import Router

from .list import router as list_router
from .view import router as view_router


__all__ = (
    'router',
)


router = Router()
router.include_routers(
    list_router,
    view_router
)
