from aiogram.fsm.state import StatesGroup, State

class RegForm(StatesGroup):
    citizenship = State()
    term = State()
    urgency = State()
    name = State()
    contact = State()
