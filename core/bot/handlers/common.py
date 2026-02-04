from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from core.bot.services.utils import return_to_main_menu

router = Router()


@router.callback_query(F.data == "back_to_main")
async def handle_back_to_main(callback: CallbackQuery, state: FSMContext):
    await return_to_main_menu(callback, state)
