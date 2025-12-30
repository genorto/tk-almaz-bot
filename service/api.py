import requests

from app.config import API_KEY, API_URL

def call_api(reg_number: str) -> list:
	params = {"key": API_KEY, "regNumber": reg_number.replace(" ", "").upper()}

	try:
		r = requests.get(API_URL, params=params, timeout=10)
	except requests.RequestException:
		return f"❌ Не удалось обратиться к сервису. Попробуйте позже."

	if r.status_code == 400:
		return f"❌ Ошибка валидации запроса."

	if r.status_code == 403:
		return f"❌ Закончились токены."

	records = r.json().get("records") or []

	if not records:
		return f"❌ Пропуск не найден."

	return records
