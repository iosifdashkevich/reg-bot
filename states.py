from aiogram.fsm.state import State, StatesGroup

class RegForm(StatesGroup):
    citizenship = State()
    term = State()
    urgency = State()
    name = State()
    contact = State()
