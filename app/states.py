from aiogram.fsm.state import State, StatesGroup

class PassCheckStates(StatesGroup):
	waiting_for_plate = State()
	waiting_for_password = State()
