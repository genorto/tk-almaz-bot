from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext

from app.states import PassCheckStates
from app.config import PASSWORD
from service.api import call_api
from service.whitelist import load_whitelist, is_user_allowed, add_user_to_whitelist

def get_handlers_router() -> Router:
	router = Router()

	auth_keyboard = [
		[KeyboardButton(text="🔐 Авторизация")]
	]

	main_menu_keyboard = [
		[KeyboardButton(text="🔍 Проверить пропуск")]
	]

	cancel_keyboard = [
		[KeyboardButton(text="❌ Отмена")]
	]

	async def check_access(message: Message) -> bool:
		if not is_user_allowed(message.from_user.id):
			await message.answer("❌ Доступ запрещён.")
			return False
		return True

	@router.message(Command("start"))
	async def cmd_start(message: Message) -> None:
		whitelist = load_whitelist()
		user_id = message.from_user.id

		if user_id not in whitelist:
			await message.answer(
				"👋 Добро пожаловать!\n\n"
				"🔐 Для доступа нажмите кнопку ниже:",
				reply_markup=ReplyKeyboardMarkup(keyboard=auth_keyboard)
			)

		else:
			await message.answer(
				"👋 Добро пожаловать!\n\nВыберите действие:",
				reply_markup=ReplyKeyboardMarkup(keyboard=main_menu_keyboard)
			)

	@router.message(F.text == "🔐 Авторизация")
	async def cmd_auth(message: Message, state: FSMContext) -> None:
		if is_user_allowed(message.from_user.id):
			await message.answer("✅ Вы уже авторизованы!")
			return
	
		await message.answer(
			"🔐 Введите пароль для доступа к боту:\n\n",
			reply_markup=ReplyKeyboardMarkup(keyboard=cancel_keyboard)
		)

		await state.set_state(PassCheckStates.waiting_for_password)


	@router.message(PassCheckStates.waiting_for_password)
	async def process_password(message: Message, state: FSMContext) -> None:
		password = message.text.strip()
		user_id = message.from_user.id

		if password == PASSWORD:
			if add_user_to_whitelist(user_id):
				await message.answer(
					"✅ Успешно! Вы добавлены в список авторизованных пользователей.",
					reply_markup=ReplyKeyboardMarkup(keyboard=main_menu_keyboard)
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
			reply_markup=ReplyKeyboardMarkup(keyboard=cancel_keyboard)
		)
		await state.set_state(PassCheckStates.waiting_for_plate)

	@router.message(PassCheckStates.waiting_for_plate)
	async def process_plate_input(message: Message, state: FSMContext) -> None:
		if not await check_access(message):
			await state.clear()
			return

		if message.text.strip() == "❌ Отмена":
			await state.clear()
			await message.answer(
				"Выберите действие:",
				reply_markup=ReplyKeyboardMarkup(keyboard=main_menu_keyboard)
			)
			return

		reply = call_api(message.text.strip())
		await message.answer(
			reply,
			reply_markup=ReplyKeyboardMarkup(keyboard=main_menu_keyboard)
		)
		await state.clear()

	return router
