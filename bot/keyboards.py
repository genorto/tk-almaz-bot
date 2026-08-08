from math import ceil

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import PLATES_PER_PAGE


def get_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔍 Проверить пропуск", callback_data="check_license"),
        InlineKeyboardButton(text="🚛 Гараж", callback_data="garage_page_1")
    )
    return builder.as_markup()

def get_garage_keyboard(plates: list, page: int) -> InlineKeyboardMarkup:
    if len(plates) == 0:
        builder = InlineKeyboardBuilder()
        builder.row(
            InlineKeyboardButton(
                text="➕ Добавить",
                callback_data="add_plate",
            ),
            InlineKeyboardButton(
                text="🏠 Меню",
                callback_data="menu",
            ),
        )
        return builder.as_markup()

    start_idx = (page - 1) * PLATES_PER_PAGE
    pages = ceil(len(plates) / PLATES_PER_PAGE)
    builder = InlineKeyboardBuilder()

    for idx in range(PLATES_PER_PAGE):
        if start_idx + idx >= len(plates):
            break

        plate = plates[start_idx + idx]["plate"]
        builder.row(
            InlineKeyboardButton(
                text=plate,
                callback_data="none",
            ),
            InlineKeyboardButton(
                text="🔍",
                callback_data=f"check:{plate}:{page}",
            ),
            InlineKeyboardButton(
                text="🗑️",
                callback_data=f"delete:{plate}:{page}",
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text="⬅️",
            callback_data=f"garage_page_{page - 1}" if page > 1 else "none",
        ),
        InlineKeyboardButton(text="➕", callback_data="add_plate"),
        InlineKeyboardButton(text="🏠", callback_data="menu"),
        InlineKeyboardButton(
            text="➡️",
            callback_data=f"garage_page_{page + 1}" if page < pages else "none",
        ),
    )

    return builder.as_markup()

def get_cancel_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="❌ Отмена", callback_data="cancel"))
    return builder.as_markup()
