import requests

from app.config import API_KEY, API_URL

def call_api(reg_number: str) -> list:
	params = {"key": API_KEY, "regNumber": reg_number.replace(" ", "").upper()}

	try:
		r = requests.get(API_URL, params=params, timeout=10)
	except requests.RequestException:
		print(f"❌ Не удалось обратиться к сервису. Попробуйте позже.")
		return []

	if r.status_code == 400:
		print(f"❌ Ошибка валидации запроса.")
		return []

	if r.status_code == 403:
		print(f"❌ Закончились токены.")
		return []

	records = r.json().get("records") or []

	if not records:
		print(f"❌ Пропуск не найден.")
		return []

	return records
