import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.config import CHECKPASS_INTERVAL
from service.users import load_users
from service.plates import (
	add_pass_to_plate,
	update_pass_from_plate,
	get_plate_passes
)
from service.api import call_api
from service.utils import calculate_remaining_days

logger = logging.getLogger(__name__)

def format_info(title: str, record: dict) -> list:
	return [
		title,
		f"📋 Номер пропуска: {record.get('licenseNumber')}",
		f"📅 Начало действия: {record.get('startDate')}",
		f"📅 Окончание действия: {record.get('endDate')}",
		f"📍 Зона действия: {record.get('allowedZona')}",
		f"📝 Тип пропуска: {record.get('licenseType')}",
		f"⏳ Тип действия: {record.get('type')}"
	]

async def send_plate_difference(bot, user_id: int, plate: str, new_passes: list) -> None:
	for new_pass in new_passes:
		old_passes = get_plate_passes(plate)
		found = False

		for old_pass in old_passes:
			if new_pass.get("licenseNumber") != old_pass.get("licenseNumber"):
				continue

			old_remaining_days = calculate_remaining_days(old_pass.get("endDate"))
			new_remaining_days = calculate_remaining_days(new_pass.get("endDate"))

			old_status = old_pass.get("status")
			new_status = new_pass.get("status")

			if old_remaining_days > 0 and new_remaining_days == 0:
				lines = format_info(
					f"На ваше ТС {plate} СЕГОДНЯ истекает срок действия пропуска:",
					new_pass
				)

				await bot.send_message(
					chat_id=user_id,
					text="\n".join(lines)
				)
			elif old_status == "Действующий" and new_status == "Истек срок действия":
				lines = format_info(
					f"На ваше ТС {plate} закончен срок действия пропуска:",
					new_pass
				)

				await bot.send_message(
					chat_id=user_id,
					text="\n".join(lines)
				)
			elif old_status == "Действующий" and new_status == "Аннулирован":
				lines = format_info(
					f"На ваше ТС {plate} аннулирован пропуск:",
					new_pass
				)

				await bot.send_message(
					chat_id=user_id,
					text="\n".join(lines)
				)

			found = True
			break

		if found:
			continue

		lines = format_info(
			f"На ваше ТС {plate} выдан новый пропуск:",
			new_pass
		)

		await bot.send_message(
			chat_id=user_id,
			text="\n".join(lines)
		)

async def check_all_tracking_plates(bot) -> None:
	try:
		users = load_users()

		if not users:
			return
		
		for user_id, plates in users.items():
			for item in plates:
				plate = item.get("plate", item)
				tracking = item.get("tracking", False)

				if not tracking:
					continue
				
				try:
					records = call_api(plate)

					await send_plate_difference(bot, user_id, plate, records)

					update_all_passes(plate, records)

					await asyncio.sleep(1)

				except Exception as e:
					logger.error(f"❌ Ошибка при проверке {plate}: {e}")

	except Exception as e:
		logger.error(f"❌ Ошибка в периодической проверке: {e}")

def start_scheduler(bot) -> AsyncIOScheduler:
	scheduler = AsyncIOScheduler()

	scheduler.add_job(
		check_all_tracking_plates,
		"interval",
		hours=CHECKPASS_INTERVAL,
		args=[bot]
	)

	scheduler.start()
	
	return scheduler
