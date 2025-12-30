import json

from app.config import PLATES_PATH

def load_plates() -> dict:
	try:
		with open(PLATES_PATH, "r") as f:
			passes = json.load(f)
		return passes
	except FileNotFoundError:
		print(f"⚠️ Файл {PLATES_PATH} не найден.")
		return {}
	except json.JSONDecodeError:
		print(f"⚠️ Ошибка при чтении JSON.")
		return {}

def save_plates(plates: dict) -> bool:
	try:
		with open(PLATES_PATH, "w") as f:
			json.dump(plates, f, indent=2)
		return True
	except IOError as e:
		print(f"❌ Ошибка при сохранении: {e}")
		return False

def exists_by_plate(plate: str) -> bool:
	return plate in load_plates()

def get_plate_passes(plate: str) -> list:
	return load_plates().get(plate, {}).get("passes", [])

def add_plate(plate: str) -> bool:
	plates = load_plates()

	if plate in plates:
		return False

	plates[plate] = {"passes": []}

	return save_plates(plates)

def add_pass_to_plate(plate: str, new_pass: dict) -> bool:
	if not exists_by_plate(plate):
		return False

	plates = load_plates()
	passes = get_plate_passes(plate)

	if not any(p == new_pass for p in passes):
		passes.append(new_pass)
		plates[plate] = {"passes": passes}
		return save_plates(plates)
	return False

def update_pass_from_plate(plate: str, new_pass: dict) -> bool:
	if not exists_by_plate(plate):
		return False

	plates = load_plates()
	passes = get_plate_passes(plate)

	for i, p in enumerate(passes):
		if p.get("licenseNumber") != new_pass.get("licenseNumber"):
			continue

		passes[i] = new_pass
		plates[plate] = {"passes": passes}
		return save_plates(plates)
	return False

def update_all_passes(plate: str, new_passes: list):
	if not exists_by_plate(plate):
		add_plate(plate)

	for new_pass in new_passes:
		old_passes = get_plate_passes(plate)
		found = False

		for old_pass in old_passes:
			if new_pass.get("licenseNumber") != old_pass.get("licenseNumber"):
				continue

			update_pass_from_plate(plate, new_pass)
			found = True
			break

		if found:
			continue

		add_pass_to_plate(plate, new_pass)
