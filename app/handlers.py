from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
	Message,
	KeyboardButton,
	ReplyKeyboardMarkup,
	InlineKeyboardButton,
	InlineKeyboardMarkup,
	CallbackQuery
)
from aiogram.fsm.context import FSMContext

from app.states import BotStates
from app.config import PASSWORD
from service.api import call_api
from service.users import (
	add_user,
	exists_by_id,
	get_user_plates,
	add_plate_to_user,
	delete_plate_from_user,
	toggle_plate_tracking,
	is_tracking
)

def get_handlers_router() -> Router:
	router = Router()

	auth_keyboard = [
		[KeyboardButton(text="🔐 Авторизация")]
	]

	mainmenu_keyboard = [
		[KeyboardButton(text="🔍 Проверить пропуск"), KeyboardButton(text="🚚 Гараж")]
	]

	garage_keyboard = [
		[KeyboardButton(text="➕ Добавить госномер")],
		[KeyboardButton(text="🏠 Главное меню")]
	]

	cancel_keyboard = [
		[KeyboardButton(text="❌ Отмена")]
	]

	async def check_access(message: Message) -> bool:
		if not exists_by_id(message.from_user.id):
			await message.answer("❌ Доступ запрещён.")
			return False
		return True

	@router.message(Command("start"))
	async def cmd_start(message: Message) -> None:
		if exists_by_id(message.from_user.id):
			await message.answer(
				"👋 Добро пожаловать!\n\n"
				"Выберите действие:",
				reply_markup=ReplyKeyboardMarkup(
					keyboard=mainmenu_keyboard,
					resize_keyboard=True
				)
			)

		else:
			await message.answer(
				"👋 Добро пожаловать!\n\n"
				"🔐 Для получения доступа нажмите кнопку ниже:",
				reply_markup=ReplyKeyboardMarkup(
					keyboard=auth_keyboard,
					resize_keyboard=True
				)
			)

	@router.message(F.text == "🔐 Авторизация")
	async def cmd_auth(message: Message, state: FSMContext) -> None:
		if exists_by_id(message.from_user.id):
			await message.answer("✅ Вы уже авторизованы!")
			return
	
		await message.answer(
			"🔐 Введите пароль для доступа к боту:\n\n",
			reply_markup=ReplyKeyboardMarkup(
				keyboard=cancel_keyboard,
				resize_keyboard=True
			)
		)

		await state.set_state(BotStates.waiting_for_password)


	@router.message(BotStates.waiting_for_password)
	async def process_password_input(message: Message, state: FSMContext) -> None:
		if message.text.strip() == PASSWORD:
			if add_user(message.from_user.id):
				await message.answer(
					"✅ Успешно! Вы добавлены в список авторизованных пользователей.",
					reply_markup=ReplyKeyboardMarkup(
						keyboard=mainmenu_keyboard,
						resize_keyboard=True
					)
				)
			else:
				await message.answer("ℹ️ Вы уже авторизованы.")
		else:
			await message.answer("❌ Неверный пароль. Попробуйте ещё раз.\n")
		await state.clear()

	@router.message(F.text == "🔍 Проверить пропуск")
	async def cmd_checkpass(message: Message, state: FSMContext) -> None:
		if not await check_access(message):
			return

		await message.answer(
			"Введите госномер автомобиля.\n"
			"Пример: А250СМ62\n\n",
			reply_markup=ReplyKeyboardMarkup(
				keyboard=cancel_keyboard,
				resize_keyboard=True
			)
		)
		await state.set_state(BotStates.waiting_for_plate)

	@router.message(BotStates.waiting_for_plate)
	async def process_plate_input(message: Message, state: FSMContext) -> None:
		if not await check_access(message):
			await state.clear()
			return

		if message.text.strip() == "❌ Отмена":
			await state.clear()
			await cmd_mainmenu(message, state)
			return
		
		await message.answer(
			call_api(message.text.strip()),
			reply_markup=ReplyKeyboardMarkup(
				keyboard=mainmenu_keyboard,
				resize_keyboard=True
			)
		)
		await state.clear()

	async def show_garage(message: Message, user_id: int) -> None:
		plates = get_user_plates(user_id)

		if not plates:
			await message.answer("ℹ️ Ваш гараж пуст.")

		else:
			await message.answer("🚚 Ваш гараж:")

			for item in plates:
				plate = item.get("plate", item)

				await message.answer(
					f"🚚 {plate}",
					reply_markup=InlineKeyboardMarkup(
						inline_keyboard=[
							[InlineKeyboardButton(
								text="🟢 Отслеживается"
								if is_tracking(message.from_user.id, plate)
								else "🔴 Не отслеживается",
								callback_data=f"toggle_plate:{plate}"
							)],
							[InlineKeyboardButton(
								text="🚫 Удалить",
								callback_data=f"delete_plate:{plate}"
							)]
						]
					)
				)

		await message.answer(
			"Выберите действие:",
			reply_markup=ReplyKeyboardMarkup(
				keyboard=garage_keyboard,
				resize_keyboard=True
			)
		)


	@router.message(F.text == "🚚 Гараж")
	async def cmd_garage(message: Message) -> None:
		if not await check_access(message):
			return

		await show_garage(message, message.from_user.id)

	@router.message(F.text == "➕ Добавить госномер")
	async def cmd_addnumber(message: Message, state: FSMContext) -> None:
		if not await check_access(message):
			return

		await message.answer(
			"Введите госномер автомобиля.\n"
			"Пример: А250СМ62\n\n",
			reply_markup=ReplyKeyboardMarkup(
				keyboard=cancel_keyboard,
				resize_keyboard=True
			)
		)
		await state.set_state(BotStates.waiting_for_number)

	@router.message(BotStates.waiting_for_number)
	async def process_number_input(message: Message, state: FSMContext) -> None:
		if not await check_access(message):
			await state.clear()
			return

		if message.text.strip() == "❌ Отмена":
			await state.clear()
			await show_garage(message, message.from_user.id)
			return
			
		if add_plate_to_user(message.from_user.id, message.text.strip()):
			await message.answer("✅ Номер добавлен успешно.")
		else:
			await message.answer("❌ Ошибка при добавлении номера.")
		await state.clear()
		await show_garage(message, message.from_user.id)

	@router.message(F.text == "🏠 Главное меню")
	async def cmd_mainmenu(message: Message, state: FSMContext) -> None:
		if not await check_access(message):
			await state.clear()
			return

		await message.answer(
			"Выберите действие:",
			reply_markup=ReplyKeyboardMarkup(
				keyboard=mainmenu_keyboard,
				resize_keyboard=True
			)
		)
		await state.clear()

	@router.callback_query(F.data.startswith("toggle_plate:"))
	async def toggle_tracking(query: CallbackQuery) -> None:
		user_id = query.from_user.id
		plate = query.data.split(":", 1)[1]

		await query.answer()

		if toggle_plate_tracking(user_id, plate):
			await query.message.edit_text(
				f"🚚 {plate}",
				reply_markup=InlineKeyboardMarkup(
					inline_keyboard=[
						[InlineKeyboardButton(
							text="🟢 Отслеживается"
							if is_tracking(user_id, plate)
							else "🔴 Не отслеживается",
							callback_data=f"toggle_plate:{plate}"
						)],
						[InlineKeyboardButton(
							text="🚫 Удалить",
							callback_data=f"delete_plate:{plate}"
						)]
					]
				)
			)

	@router.callback_query(F.data.startswith("delete_plate:"))
	async def delete_plate(query: CallbackQuery) -> None:
		user_id = query.from_user.id
		plate = query.data.split(":", 1)[1]

		await query.answer()

		if delete_plate_from_user(user_id, plate):
			await query.message.delete()

	return router
