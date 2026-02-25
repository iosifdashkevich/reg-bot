from aiogram.fsm.state import StatesGroup, State


class RegForm(StatesGroup):
    citizenship = State()   # выбор гражданства
    term = State()          # выбор срока
    urgency = State()       # срочность
    consent = State()       # согласие на обработку данных
    name = State()          # имя клиента
    contact = State()       # телефон / контакт
class AdminReply(StatesGroup):
    waiting_for_message = State()
