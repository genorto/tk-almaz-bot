from math import ceil

from aiogram import F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    InlineKeyboardMarkup,
    Message,
)
from aiogram.utils.chat_action import ChatActionSender

from config import PLATES_PER_PAGE
from db.repository import (
    add_plate_to_user,
    add_user,
    delete_plate_from_user,
    get_user_plates,
    remove_user,
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

@router.my_chat_member()
async def on_bot_blocked(update: ChatMemberUpdated) -> None:
    if update.chat.type == "private" and update.new_chat_member.status == ChatMemberStatus.KICKED:
        await remove_user(str(update.chat.id))

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
    await state.update_data(prompt_message_id=callback.message.message_id)

@router.message(CheckLicense.plate)
async def process_plate_input(msg: Message, state: FSMContext) -> None:
    data = await state.get_data()
    prompt_message_id = data["prompt_message_id"]
    plate = msg.text.replace(" ", "").upper()

    await msg.delete()
    await msg.bot.delete_message(chat_id=msg.chat.id, message_id=prompt_message_id)

    async with ChatActionSender.typing(bot=msg.bot, chat_id=msg.chat.id):
        licenses = await call_api(plate)

        await msg.answer(
            format_licenses(licenses, plate),
            disable_notification=False,
        )

    await msg.answer(
        "🏠 Меню",
        reply_markup=get_menu_keyboard(),
    )
    await state.clear()

async def _render_garage(user_id: str, page: int) -> tuple[str, InlineKeyboardMarkup]:
    plates = await get_user_plates(user_id)
    if plates:
        pages = ceil(len(plates) / PLATES_PER_PAGE)
        page = min(max(page, 1), pages)
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
    current_state = await state.get_state()
    await state.clear()

    if current_state == AddPlate.plate.state:
        text, keyboard = await _render_garage(str(callback.from_user.id), 1)
    else:
        text, keyboard = "🏠 Меню", get_menu_keyboard()

    await callback.message.edit_text(text, reply_markup=keyboard)
    await callback.answer()

@router.callback_query(F.data == "add_plate")
async def cmd_add_plate(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.message.edit_text(
        "Введите госномер автомобиля.\nПример: А250СМ62",
        reply_markup=get_cancel_keyboard(),
    )
    await callback.answer()
    await state.set_state(AddPlate.plate)
    await state.update_data(prompt_message_id=callback.message.message_id)

@router.message(AddPlate.plate)
async def process_add_plate(msg: Message, state: FSMContext) -> None:
    data = await state.get_data()
    prompt_message_id = data["prompt_message_id"]
    plate = msg.text.replace(" ", "").upper()

    await add_plate_to_user(str(msg.from_user.id), plate)
    await msg.delete()

    text, keyboard = await _render_garage(str(msg.from_user.id), 1)
    await msg.bot.edit_message_text(
        text,
        chat_id=msg.chat.id,
        message_id=prompt_message_id,
        reply_markup=keyboard,
    )
    await state.clear()

@router.callback_query(F.data.startswith("check:"))
async def check_garage_plate(callback: CallbackQuery) -> None:
    _, plate, page = callback.data.split(":")
    await callback.answer("Проверяем пропуск...")
    await callback.message.delete()

    async with ChatActionSender.typing(bot=callback.bot, chat_id=callback.message.chat.id):
        licenses = await call_api(plate)
        await update_car_licenses(plate, licenses)

        await callback.message.answer(
            format_licenses(licenses, plate),
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
