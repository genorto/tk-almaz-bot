from datetime import datetime

def calculate_remaining_days(end_date_str: str) -> int:
	end_date = datetime.strptime(end_date_str, "%d.%m.%Y").date()
	today = datetime.now().date()
	return (end_date - today).days

def is_valid(record: dict) -> bool:
	end_date = record.get('endDate')
	remaining_days = calculate_remaining_days(end_date)
	cancellation_date = record.get('cancellationDate')
	return remaining_days >= 0 and not cancellation_date

def format_record(record: dict) -> str:
	lines = [
		f"📋 Номер пропуска: {record.get('licenseNumber')}",
		f"🚛 ГРЗ: {record.get('regNumber')}",
		f"📅 Начало действия: {record.get('startDate')}",
		f"📅 Окончание действия: {record.get('endDate')}",
		f"📍 Зона действия: {record.get('allowedZona')}",
		f"📝 Тип пропуска: {record.get('licenseType')}",
		f"⏳ Тип действия: {record.get('type')}",
		f"🔍 Статус пропуска: {record.get('status')}",
	]

	remaining_days = calculate_remaining_days(record.get('endDate'))

	if remaining_days == 0:
		lines.append(f"⚠️ Пропуск истекает сегодня.")
	else:
		lines.append(f"⏳ Осталось дней действия: {remaining_days}")

	return "\n".join(lines)

def format_records(records: list) -> str:
	valid_records = [format_record(r) for r in records if is_valid(r)]

	if not valid_records:
		return "❌ Активные пропуска не найдены."

	return "\n\n---\n\n".join(valid_records[:2])
