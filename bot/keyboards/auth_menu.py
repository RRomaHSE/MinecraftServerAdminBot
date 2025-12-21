from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_auth_main_keyboard() -> InlineKeyboardMarkup:
    """Mеню авторизации для неавторизованных пользователей"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔐 Авторизоваться", callback_data="auth_start"),
        InlineKeyboardButton(text="❓ Помощь", callback_data="help"),
    )

    return builder.as_markup()


def get_auth_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="❌ Отмена", callback_data="auth_cancel"),
    )

    return builder.as_markup()


def get_auth_success_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура после успешной авторизации"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="📊 Статус сервера", callback_data="status"),
        InlineKeyboardButton(text="⚡ Быстрые команды", callback_data="quick_commands"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Сменить сервер", callback_data="auth_change_server"),
        InlineKeyboardButton(text="🚪 Выйти", callback_data="auth_logout"),
    )

    return builder.as_markup()


def get_session_manage_keyboard() -> InlineKeyboardMarkup:
    """Управление сессией"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔄 Сменить сервер", callback_data="auth_change_server"),
        InlineKeyboardButton(text="➕ Добавить сервер", callback_data="auth_add_server"),
    )
    builder.row(
        InlineKeyboardButton(text="🚪 Выйти", callback_data="auth_logout"),
        InlineKeyboardButton(text="↩️ Назад", callback_data="main_menu"),
    )

    return builder.as_markup()


def get_auth_retry_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура при ошибке авторизации"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="🔄 Попробовать снова", callback_data="auth_retry"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="main_menu"),
    )

    return builder.as_markup()


def get_password_toggle_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для скрытия/показа пароля"""
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(text="👁️ Показать/Скрыть", callback_data="auth_toggle_password"),
        InlineKeyboardButton(text="❌ Отмена", callback_data="auth_cancel"),
    )

    return builder.as_markup()