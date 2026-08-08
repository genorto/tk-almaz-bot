from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.chat_action import ChatActionSender

from db.repository import (
    add_plate_to_user,
    add_user,
    delete_plate_from_user,
    get_user_plates,
    update_car_licenses,
)
from services.formatting import format_licenses
from services.license_api import call_api

from .keyboards import get_cancel_keyboard, get_garage_keyboard, get_menu_keyboard
from .states import AddPlate, CheckLicense

router = Router()

@router.message(CommandStart())
async def cmd_start(msg: Message) -> None:
    await add_user(str(msg.from_user.id))
    await msg.answer(
        "👋 Добро пожаловать!",
        reply_markup=get_menu_keyboard(),
        disable_notification=False,
    )

@router.callback_query(F.data == "menu")
async def show_menu(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        "🏠 Меню",
        reply_markup=get_menu_keyboard(),
    )
    await callback.answer()

@router.callback_query(F.data == "check_license")
async def cmd_check_license(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "Введите госномер автомобиля.\nПример: А250СМ62",
        reply_markup=get_cancel_keyboard(),
    )
    await callback.answer()
    await state.set_state(CheckLicense.plate)

@router.message(CheckLicense.plate)
async def process_plate_input(msg: Message, state: FSMContext) -> None:
    async with ChatActionSender.typing(bot=msg.bot, chat_id=msg.chat.id):
        plate = msg.text.replace(" ", "").upper()

        licenses = await call_api(plate)

        await msg.reply(
            format_licenses(licenses),
            disable_notification=False,
        )
        await msg.answer(
            "🏠 Меню",
            reply_markup=get_menu_keyboard(),
            disable_notification=True,
        )
    await state.clear()

async def _render_garage(user_id: str, page: int) -> tuple[str, InlineKeyboardMarkup]:
    plates = await get_user_plates(user_id)
    text = "🚛 Ваш гараж" if plates else "ℹ️ Ваш гараж пуст."
    return text, get_garage_keyboard(plates, page)

@router.callback_query(F.data.startswith("garage_page_"))
async def show_garage(callback: CallbackQuery) -> None:
    user_id = str(callback.from_user.id)
    page = int(callback.data.removeprefix("garage_page_"))

    text, keyboard = await _render_garage(user_id, page)
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "none")
async def noop(callback: CallbackQuery) -> None:
    await callback.answer()

@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await callback.message.edit_text(
        "🏠 Меню",
        reply_markup=get_menu_keyboard(),
    )
    await callback.answer()

@router.callback_query(F.data == "add_plate")
async def cmd_add_plate(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "Введите госномер автомобиля.\nПример: А250СМ62",
        reply_markup=get_cancel_keyboard(),
    )
    await callback.answer()
    await state.set_state(AddPlate.plate)

@router.message(AddPlate.plate)
async def process_add_plate(msg: Message, state: FSMContext) -> None:
    plate = msg.text.replace(" ", "").upper()
    await add_plate_to_user(str(msg.from_user.id), plate)
    await state.clear()

    text, keyboard = await _render_garage(str(msg.from_user.id), 1)
    await msg.answer(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("check:"))
async def check_garage_plate(callback: CallbackQuery) -> None:
    _, plate, page = callback.data.split(":")
    await callback.answer("Проверяем пропуск...")

    async with ChatActionSender.typing(bot=callback.bot, chat_id=callback.message.chat.id):
        licenses = await call_api(plate)
        await update_car_licenses(plate, licenses)

        await callback.message.answer(
            format_licenses(licenses),
            disable_notification=False,
        )

    text, keyboard = await _render_garage(str(callback.from_user.id), int(page))
    await callback.message.answer(text, reply_markup=keyboard)

@router.callback_query(F.data.startswith("delete:"))
async def delete_garage_plate(callback: CallbackQuery) -> None:
    _, plate, page = callback.data.split(":")
    await delete_plate_from_user(str(callback.from_user.id), plate)

    text, keyboard = await _render_garage(str(callback.from_user.id), int(page))
    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()
