from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.main_menu import get_main_menu_keyboard

router = Router()


@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    welcome_text = (
        "🏠 *Главное меню*\n\n"
        "👇 Выберите действие:"
    )

    await callback.message.edit_text(
        welcome_text,
        parse_mode="Markdown",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()