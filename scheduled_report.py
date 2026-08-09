import asyncio

from aiogram import Bot

from config import BOT_TOKEN, TIMEOUT, db
from db.repository import get_licenses_for_car, get_tracked_plates, update_car_licenses
from services.formatting import calculate_remaining_days
from services.license_api import call_api


def format_title(old_passes: list, new_pass: dict) -> str | None:
    plate = new_pass.get("regNumber")

    for old_pass in old_passes:
        if new_pass.get("licenseNumber") != old_pass.get("license_number"):
            continue

        old_days = calculate_remaining_days(old_pass.get("end_date"))
        new_days = calculate_remaining_days(new_pass.get("endDate"))

        if old_days > 0 and new_days == 0:
            return f"🔔 На ваше ТС {plate} СЕГОДНЯ истекает срок действия пропуска:"

        if new_pass.get("status") == "Действующий" and old_days > 30 and new_days == 30:
            return f"🔔 Через 30 дней истекает срок действия пропуска на ваше ТС {plate}:"

        if new_pass.get("status") == "Действующий" and old_days > 60 and new_days == 60:
            return f"🔔 Через 60 дней истекает срок действия пропуска на ваше ТС {plate}:"

        old_status = old_pass.get("status")
        new_status = new_pass.get("status")

        if old_status == "Действующий" and new_status == "Истек срок действия":
            return f"🔔 На ваше ТС {plate} истек срок действия пропуска:"

        if old_status == "Действующий" and new_status == "Аннулирован":
            return f"🔔 На ваше ТС {plate} аннулирован пропуск:"

        return None

    if new_pass.get("status") == "Действующий":
        return f"🔔 На ваше ТС {plate} выдан новый пропуск:"


def format_report(old_passes: list, new_pass: dict) -> str | None:
    title = format_title(old_passes, new_pass)

    if title is None:
        return None

    return "\n".join(
        [
            title,
            f"📋 Номер пропуска: {new_pass.get('licenseNumber')}",
            f"📅 Начало действия: {new_pass.get('startDate')}",
            f"📅 Окончание действия: {new_pass.get('endDate')}",
            f"📍 Зона действия: {new_pass.get('allowedZona')}",
            f"📝 Тип пропуска: {new_pass.get('licenseType')}",
            f"⏳ Тип действия: {new_pass.get('type')}",
        ]
    )


async def send_report(bot: Bot, user_id: str, old_passes: list, new_passes: list) -> None:
    for new_pass in new_passes:
        text = format_report(old_passes, new_pass)

        if text is None:
            continue

        await bot.send_message(chat_id=user_id, text=text)


async def check_tracked_plates(bot: Bot) -> None:
    tracked = await get_tracked_plates()

    plates_to_owners: dict[str, list[str]] = {}
    for item in tracked:
        plates_to_owners.setdefault(item["number"], []).append(item["owner"])

    for plate, owners in plates_to_owners.items():
        old_passes = await get_licenses_for_car(plate)
        new_passes = await call_api(plate)

        if new_passes:
            for owner in owners:
                await send_report(bot, owner, old_passes, new_passes)

        await update_car_licenses(plate, new_passes)
        await asyncio.sleep(TIMEOUT)


async def main():
    bot = Bot(BOT_TOKEN)
    await db.connect()
    try:
        await check_tracked_plates(bot)
    finally:
        await db.close()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
