import json
from app.config import WHITELIST_PATH

def load_whitelist() -> set:
	try:
		with open(WHITELIST_PATH, "r") as f:
			data = json.load(f)
		return set(data.get("allowed_users", []))
	except FileNotFoundError:
		print(f"⚠️ Файл {WHITELIST_PATH} не найден.")
		return set()
	except json.JSONDecodeError:
		print(f"⚠️ Ошибка при чтении JSON.")
		return set()

def save_whitelist(user_ids: set) -> bool:
	try:
		data = {"allowed_users": list(user_ids)}
		with open(WHITELIST_PATH, "w") as f:
			json.dump(data, f, indent=2)
		print(f"✅ Белый список сохранён.")
		return True
	except Exception as e:
		print(f"❌ Ошибка при сохранении: {e}")
		return False

def add_user_to_whitelist(user_id: int) -> bool:
	whitelist = load_whitelist()
	if user_id in whitelist:
		return False
	whitelist.add(user_id)
	return save_whitelist(whitelist)

def remove_user_from_whitelist(user_id: int) -> bool:
	whitelist = load_whitelist()
	if user_id not in whitelist:
		return False
	whitelist.remove(user_id)
	return save_whitelist(whitelist)

def is_user_allowed(user_id: int) -> bool:
	return user_id in load_whitelist()
