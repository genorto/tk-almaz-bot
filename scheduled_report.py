import asyncio

from aiogram import Bot

from service.users import load_users
from service.plates import update_all_passes, get_plate_passes
from service.api import call_api
from service.utils import calculate_remaining_days

from app.config import BOT_TOKEN

def format_title(plate: str, new_pass: dict) -> str | None:
	old_passes = get_plate_passes(plate)

	for old_pass in old_passes:
		if new_pass.get("licenseNumber") != old_pass.get("licenseNumber"):
			continue

		old_days = calculate_remaining_days(old_pass.get("endDate"))
		new_days = calculate_remaining_days(new_pass.get("endDate"))

		if old_days > 0 and new_days == 0:
			return f"На ваше ТС {plate} СЕГОДНЯ истекает срок действия пропуска:"

		old_status = old_pass.get("status")
		new_status = new_pass.get("status")

		if old_status == "Действующий" and new_status == "Истек срок действия":
			return f"На ваше ТС {plate} истек срок действия пропуска:"
		elif old_status == "Действующий" and new_status == "Аннулирован":
			return f"На ваше ТС {plate} аннулирован пропуск:"
		else:
			return

	if new_pass.get("status") == "Действующий":
		return f"На ваше ТС {plate} выдан новый пропуск:"

def format_report(plate: str, new_pass: dict) -> str | None:
	title = format_title(plate, new_pass)

	if not title:
		return

	return "\n".join([
		title,
		f"📋 Номер пропуска: {new_pass.get('licenseNumber')}",
		f"📅 Начало действия: {new_pass.get('startDate')}",
		f"📅 Окончание действия: {new_pass.get('endDate')}",
		f"📍 Зона действия: {new_pass.get('allowedZona')}",
		f"📝 Тип пропуска: {new_pass.get('licenseType')}",
		f"⏳ Тип действия: {new_pass.get('type')}"
	])

async def send_report(bot, user_id: str, plate: str, new_passes: list) -> None:
	text = format_report(plate, new_passes[0])

	if not text:
		return

	await bot.send_message(chat_id=user_id, text=text)

async def check_tracking_plates(bot) -> None:
	users = load_users()

	if not users:
		return
		
	for user_id, plates in users.items():
		for item in plates.get("plates"):
			tracking = item.get("tracking", False)

			if not tracking:
				continue
				
			plate = item.get("plate", item)

			records = call_api(plate)

			if records:
				await send_report(bot, user_id, plate, records)

			update_all_passes(plate, records)

async def main():
	bot = Bot(BOT_TOKEN)
	try:
		await check_tracking_plates(bot)
	finally:
		await bot.session.close()

if __name__ == "__main__":
	asyncio.run(main())
