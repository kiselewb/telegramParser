from aiogram import Router, F
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
)

from core.bot.services.keyboards import (
    back_menu_button,
    cancel_button,
    build_delete_keyboard,
)
from core.bot.states.exclude_keywords import ExcludeKeywordsFSM
from services.parser_data_manager import ParserDataManager

router = Router()
pdm = ParserDataManager()


@router.callback_query(F.data == "edit_exclude_keywords")
async def handle_edit_exclude_keywords(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    kb_buttons = [
        [
            InlineKeyboardButton(
                text="Добавить новые фразы", callback_data="add_exclude_keywords"
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить текущие фразы", callback_data="change_exclude_keywords"
            )
        ],
        back_menu_button(),
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)

    await callback.message.edit_text(text="Выберите действие:", reply_markup=kb)

    await callback.answer()


@router.callback_query(F.data == "add_exclude_keywords")
async def handle_add_exclude_keywords(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ExcludeKeywordsFSM.waiting_new_keywords)

    await callback.message.edit_text(
        text="Введите новые фразы <b>(каждая фраза с новой строки)</b>:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[cancel_button("edit_exclude_keywords")]
        ),
    )

    await callback.answer()


@router.message(StateFilter(ExcludeKeywordsFSM.waiting_new_keywords))
async def handle_set_new_exclude_keywords(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Ключевые фразы должны содержать только текст.")
        return

    new_keywords = message.text.strip().split("\n")
    all_keywords = await pdm.add_exclude_keywords(new_keywords)
    formatted = "\n".join([f"{i + 1}. {kw}" for i, kw in enumerate(all_keywords)])

    await message.answer(
        text=f"""✅ <b>Ключевые фразы успешно добавлены</b>

<b>Список всех фраз ({len(all_keywords)}):</b>
{formatted}
        """,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[back_menu_button()]),
    )

    await state.clear()


@router.callback_query(F.data == "change_exclude_keywords")
async def handle_change_exclude_keywords(callback: CallbackQuery, state: FSMContext):
    current_data = pdm.get_exclude_keywords()
    all_keywords = {str(i): keyword for i, keyword in enumerate(current_data)}

    if not all_keywords:
        await callback.answer("Нет ключевых фраз для удаления", show_alert=True)
        return

    await state.set_state(ExcludeKeywordsFSM.selecting_keywords_to_delete)
    await state.update_data(selected_for_deletion=[], all_keywords=all_keywords)

    await callback.message.edit_text(
        text="Выберите фразы, которые хотите <b>удалить</b>:",
        reply_markup=build_delete_keyboard(
            all_keywords=all_keywords,
            selected=[],
            callback_to_return="edit_exclude_keywords",
        ),
    )
    await callback.answer()


@router.callback_query(
    StateFilter(ExcludeKeywordsFSM.selecting_keywords_to_delete),
    F.data.startswith("toggle_delete:"),
)
async def handle_toggle_delete_exclude_keywords(
    callback: CallbackQuery, state: FSMContext
):
    kw_id = callback.data.split(":", 1)[1]

    data = await state.get_data()
    selected_id = data.get("selected_for_deletion", [])
    all_keywords = data.get("all_keywords", {})

    if kw_id in selected_id:
        selected_id.remove(kw_id)
    else:
        selected_id.append(kw_id)

    await state.update_data(selected_for_deletion=selected_id)

    await callback.message.edit_reply_markup(
        reply_markup=build_delete_keyboard(
            all_keywords=all_keywords,
            selected=selected_id,
            callback_to_return="edit_exclude_keywords",
        )
    )
    await callback.answer()


@router.callback_query(
    F.data == "confirm_delete",
    StateFilter(ExcludeKeywordsFSM.selecting_keywords_to_delete),
)
async def handle_confirm_delete_exclude_keywords(
    callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    selected_id = data.get("selected_for_deletion", [])
    all_keywords = data.get("all_keywords", {})

    if not selected_id:
        await callback.answer("Ничего не выбрано для удаления", show_alert=True)
        return

    keywords_to_remove = [
        keyword for kw_id, keyword in all_keywords.items() if kw_id in selected_id
    ]

    await pdm.remove_exclude_keywords(keywords_to_remove)

    new_keywords = pdm.get_exclude_keywords()
    formatted = "\n".join([f"{i + 1}. {kw}" for i, kw in enumerate(new_keywords)])

    await state.clear()
    await callback.message.edit_text(
        text=f"""✅ <b>Удалено фраз: {len(selected_id)}</b>

<b>Оставшиеся фразы ({len(new_keywords)}):</b>
{formatted if new_keywords else "<i>Нет фраз</i>"}
        """,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[back_menu_button()]),
    )
    await callback.answer()
