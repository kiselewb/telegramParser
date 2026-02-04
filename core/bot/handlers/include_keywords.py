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
from core.bot.states.include_keywords import IncludeKeywordsFSM
from services.parser_data_manager import ParserDataManager

router = Router()
pdm = ParserDataManager()


@router.callback_query(F.data == "edit_include_keywords")
async def handle_select_category_for_edit_include_keywords(
    callback: CallbackQuery, state: FSMContext
):
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

    await state.set_state(IncludeKeywordsFSM.selecting_category)

    await callback.message.edit_text(
        text="Выберите категорию ключевых фраз, которые хотите изменить:",
        reply_markup=kb,
    )

    await callback.answer()


@router.callback_query(
    StateFilter(IncludeKeywordsFSM.selecting_category), F.data.startswith("data_id")
)
async def handle_edit_include_keywords(callback: CallbackQuery, state: FSMContext):
    data_id = int(callback.data.split(":")[1])

    current_data = pdm.get_parser_data_by_id(data_id)

    await state.update_data(data_id=data_id, category=current_data["category"])

    kb_buttons = [
        [
            InlineKeyboardButton(
                text="Добавить новые фразы", callback_data="add_include_keywords"
            )
        ],
        [
            InlineKeyboardButton(
                text="Изменить текущие фразы", callback_data="change_include_keywords"
            )
        ],
        back_menu_button(),
    ]
    kb = InlineKeyboardMarkup(inline_keyboard=kb_buttons)

    await callback.message.edit_text(text="Выберите действие:", reply_markup=kb)

    await callback.answer()


@router.callback_query(F.data == "add_include_keywords")
async def handle_add_include_keywords(callback: CallbackQuery, state: FSMContext):
    await state.set_state(IncludeKeywordsFSM.waiting_new_keywords)

    await callback.message.edit_text(
        text="Введите новые фразы <b>(каждая фраза с новой строки)</b>:",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[cancel_button("edit_include_keywords")]
        ),
    )

    await callback.answer()


@router.message(StateFilter(IncludeKeywordsFSM.waiting_new_keywords))
async def handle_set_new_include_keywords(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Ключевые фразы должны содержать только текст.")
        return

    data = await state.get_data()

    new_keywords = message.text.strip().split("\n")
    all_keywords = await pdm.add_include_keywords(new_keywords, data.get("data_id"))
    formatted = "\n".join([f"{i + 1}. {kw}" for i, kw in enumerate(all_keywords)])

    await message.answer(
        text=f"""✅ <b>Ключевые фразы успешно добавлены</b>

<b>Список всех фраз ({len(all_keywords)}):</b>
{formatted}
                """,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[back_menu_button()]),
    )

    await state.clear()


@router.callback_query(F.data == "change_include_keywords")
async def handle_change_include_keywords(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    current_data = pdm.get_parser_data_by_id(data.get("data_id"))
    all_keywords = {
        str(i): keyword for i, keyword in enumerate(current_data.get("keywords"))
    }

    if not all_keywords:
        await callback.answer("Нет ключевых фраз для удаления", show_alert=True)
        return

    await state.set_state(IncludeKeywordsFSM.selecting_keywords_to_delete)
    await state.update_data(selected_for_deletion=[], all_keywords=all_keywords)

    await callback.message.edit_text(
        text="Выберите фразы, которые хотите <b>удалить</b>:",
        reply_markup=build_delete_keyboard(
            all_keywords=all_keywords,
            selected=[],
            callback_to_return="edit_include_keywords",
        ),
    )
    await callback.answer()


@router.callback_query(
    StateFilter(IncludeKeywordsFSM.selecting_keywords_to_delete),
    F.data.startswith("toggle_delete:"),
)
async def handle_toggle_delete_include_keywords(
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
            callback_to_return="edit_include_keywords",
        )
    )
    await callback.answer()


@router.callback_query(
    StateFilter(IncludeKeywordsFSM.selecting_keywords_to_delete),
    F.data == "confirm_delete",
)
async def handle_confirm_delete_include_keywords(
    callback: CallbackQuery, state: FSMContext
):
    data = await state.get_data()
    selected_id = data.get("selected_for_deletion", [])
    all_keywords = data.get("all_keywords", {})
    data_id = data.get("data_id")

    if not selected_id:
        await callback.answer("Ничего не выбрано для удаления", show_alert=True)
        return

    keywords_to_remove = [
        keyword for kw_id, keyword in all_keywords.items() if kw_id in selected_id
    ]

    await pdm.remove_include_keywords(keywords_to_remove, data_id)

    new_data = pdm.get_parser_data_by_id(data_id)
    new_keywords = new_data.get("keywords")
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
