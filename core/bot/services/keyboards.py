from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📂 Изменить скрипты", callback_data="edit_templates"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📗 Ключевые фразы", callback_data="edit_include_keywords"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📕 Исключающие ключевые фразы",
                    callback_data="edit_exclude_keywords",
                )
            ],
        ]
    )


def back_menu_button() -> list[InlineKeyboardButton]:
    return [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]


def cancel_button(
    callback_to_return: str = "back_to_main",
) -> list[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(
            text="❌ Отменить действие", callback_data=callback_to_return
        )
    ]


def build_delete_keyboard(
    all_keywords: dict[str, str],
    selected: list[str],
    callback_to_return: str = "back_to_main",
) -> InlineKeyboardMarkup:
    kb_buttons = []

    for kw_id, keyword in all_keywords.items():
        prefix = "❌" if kw_id in selected else "⬜"
        kb_buttons.append(
            [
                InlineKeyboardButton(
                    text=f"{prefix} {keyword}", callback_data=f"toggle_delete:{kw_id}"
                )
            ]
        )

    kb_buttons.append(
        [
            InlineKeyboardButton(
                text=f"🗑 Удалить выбранные ({len(selected)})",
                callback_data="confirm_delete",
            )
        ]
    )
    kb_buttons.append(cancel_button(callback_to_return))

    return InlineKeyboardMarkup(inline_keyboard=kb_buttons)
