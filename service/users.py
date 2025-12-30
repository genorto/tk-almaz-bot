import json

from app.config import USERS_PATH

def load_users() -> dict:
	try:
		with open(USERS_PATH, "r") as f:
			users = json.load(f)
		return users
	except FileNotFoundError:
		print(f"⚠️ Файл {USERS_PATH} не найден.")
		return {}
	except json.JSONDecodeError:
		print(f"⚠️ Ошибка при чтении JSON.")
		return {}

def save_users(users: dict) -> bool:
	try:
		with open(USERS_PATH, "w") as f:
			json.dump(users, f, indent=2)
		return True
	except IOError as e:
		print(f"❌ Ошибка при сохранении: {e}")
		return False

def add_user(user_id: int) -> bool:
	user_id = str(user_id)
	users = load_users()

	if user_id in users:
		return False

	users[user_id] = {"plates": []}

	return save_users(users)

def exists_by_id(user_id: int) -> bool:
	return str(user_id) in load_users()

def get_user_plates(user_id: int) -> list:
	return load_users().get(str(user_id), {}).get("plates", [])

def add_plate_to_user(user_id: int, plate: str) -> bool:
	if not exists_by_id(user_id):
		return False

	plate = plate.replace(" ", "").upper()
	users = load_users()
	plates = get_user_plates(user_id)

	if not any(p.get("plate", p) == plate for p in plates):
		plates.append({"plate": plate, "tracking": True})
		users[str(user_id)]["plates"] = plates
		return save_users(users)
	return False

def delete_plate_from_user(user_id: int, plate: str) -> bool:
	if not exists_by_id(user_id):
		return False

	plate = plate.replace(" ", "").upper()
	users = load_users()
	plates = get_user_plates(user_id)

	for i, item in enumerate(plates):
		current_plate = item.get("plate", item)
		if current_plate == plate:
			plates.pop(i)
			users[str(user_id)]["plates"] = plates
			return save_users(users)
	return False

def toggle_plate_tracking(user_id: int, plate: str) -> bool:
	if not exists_by_id(user_id):
		return False

	plate = plate.replace(" ", "").upper()
	users = load_users()
	plates = get_user_plates(user_id)

	for i, item in enumerate(plates):
		current_plate = item.get("plate", item)
		current_tracking = item.get("tracking", False)
		if current_plate == plate:
			plates[i] = {"plate": plate, "tracking": not current_tracking}
			users[str(user_id)]["plates"] = plates
			return save_users(users)
	return False

def is_tracking(user_id: int, plate: str) -> bool:
	if not exists_by_id(user_id):
		return False

	plate = plate.replace(" ", "").upper()
	users = load_users()
	plates = get_user_plates(user_id)

	for item in plates:
		current_plate = item.get("plate", item)
		current_tracking = item.get("tracking", False)
		if current_plate == plate:
			return current_tracking
	return False
