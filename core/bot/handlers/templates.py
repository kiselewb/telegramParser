from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)

from core.bot.services.keyboards import back_menu_button, cancel_button
from core.bot.states.templates import TemplateFSM
from services.parser_data_manager import ParserDataManager
from database.db_manager import DBManager


router = Router()
pdm = ParserDataManager(DBManager())


@router.callback_query(F.data == "edit_templates")
async def handle_edit_templates(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    parser_data = pdm.get_parser_data()

    kb_buttons = [
        [
            InlineKeyboardButton(
                text=f"{data.get('category')}",
                callback_data=f"data_id:{data.get('id')}",
            )
        ]
        for data in parser_data
    ]
    kb_buttons.append(back_menu_button())
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)

    await callback.message.edit_text(
        text="Выберите категорию скрипта, который хотите изменить:", reply_markup=kb
    )

    await callback.answer()


@router.callback_query(F.data.startswith("data_id"))
async def handle_edit_template_by_id(callback: CallbackQuery, state: FSMContext):
    data_id = int(callback.data.split(":")[1])

    current_data = pdm.get_parser_data_by_id(data_id)

    await state.set_state(TemplateFSM.waiting_new_template)
    await state.update_data(data_id=data_id)

    await callback.message.edit_text(
        text=f"""
        <b>Текущий скрипт для категории {current_data.get("category")}:</b>
        <i>{current_data.get("template")}</i>
        
Введите новый скрипт для этой категории:
        """,
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[cancel_button("edit_templates")]
        ),
    )

    await callback.answer()


@router.message(StateFilter(TemplateFSM.waiting_new_template))
async def handle_set_new_template(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Скрипт должен содержать текст.")
        return

    data = await state.get_data()
    data_id = data.get("data_id")
    new_template = message.text.strip()

    new_data = await pdm.update_parser_data_by_id(
        data={"template": new_template}, parser_data_id=data_id
    )

    await message.answer(
        text=f"""
    ✅ <b>Скрипт успешно обновлён</b>
    
    <b>Категория:</b> {new_data.get("category")}
    <b>Новый скрипт:</b> {new_data.get("template")}
    """,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[back_menu_button()]),
    )

    await state.clear()
