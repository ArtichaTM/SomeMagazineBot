from aiogram import Router

from .main import router as main_router


__all__ = (
    'router',
)


router = Router()
router.include_routers(
    main_router
)
