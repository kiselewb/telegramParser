from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import Command

from core.bot.services.keyboards import main_menu_kb


router = Router()


@router.message(Command("start"))
async def handle_start(message: Message, state: FSMContext):
    await state.clear()
    text = """
    👋 Привет! Я бот, который поможет тебе изменить скрипты и ключевые фразы для твоего парсера!
Выберите необходимое действие
    """
    await message.answer(text, reply_markup=main_menu_kb())
