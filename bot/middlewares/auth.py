from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from bot.services.session_manager import session_manager


class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки авторизации"""

    def __init__(self):
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message | CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id

        # Команды, доступные только авторизованным
        protected_commands = ["status", "quick_commands", "monitoring",
                              "notifications", "auth_manage_session",
                              "auth_logout", "auth_change_server"]

        if isinstance(event, CallbackQuery) and event.data in protected_commands:
            if not session_manager.is_authorized(user_id):
                await event.answer(
                    "🔒 Доступ ограничен. Используйте /start для авторизации.",
                    show_alert=True
                )
                return

        return await handler(event, data)