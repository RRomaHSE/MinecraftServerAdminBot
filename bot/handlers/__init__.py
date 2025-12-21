from aiogram import Router

router = Router()

from .start import router as start_router
from .help import router as help_router
from .status import router as status_router
from .auth import router as auth_router

router.include_router(start_router)
router.include_router(help_router)
router.include_router(status_router)
router.include_router(auth_router)

__all__ = ['router']