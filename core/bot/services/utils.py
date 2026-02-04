from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core.bot.services.keyboards import main_menu_kb


async def return_to_main_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text="🏠 Главное меню", reply_markup=main_menu_kb()
    )
    await callback.answer()
