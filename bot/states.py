from aiogram.fsm.state import State, StatesGroup


class CheckLicense(StatesGroup):
    plate = State()


class AddPlate(StatesGroup):
    plate = State()
