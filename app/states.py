from aiogram.fsm.state import State, StatesGroup

class BotStates(StatesGroup):
	waiting_for_plate = State()
	waiting_for_password = State()
	waiting_for_number = State()
