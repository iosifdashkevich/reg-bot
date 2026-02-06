from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states import RegForm
from keyboards import citizenship_kb, term_kb, urgency_kb, contact_kb, remove_kb
from config import ADMIN_ID

router = Router()


@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegForm.citizenship)
    await message.answer("Выберите ваш статус:", reply_markup=citizenship_kb())


@router.message(RegForm.citizenship)
async def step_citizenship(message: Message, state: FSMContext):
    await state.update_data(citizenship=message.text)
    await state.set_state(RegForm.term)
    await message.answer("Выберите срок регистрации:", reply_markup=term_kb())


@router.message(RegForm.term)
async def step_term(message: Message, state: FSMContext):
    await state.update_data(term=message.text)
    await state.set_state(RegForm.urgency)
    await message.answer("Когда нужно оформить?", reply_markup=urgency_kb())


@router.message(RegForm.urgency)
async def step_urgency(message: Message, state: FSMContext):
    await state.update_data(urgency=message.text)
    await state.set_state(RegForm.name)
    await message.answer("Введите ваше имя:", reply_markup=remove_kb())


@router.message(RegForm.name)
async def step_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegForm.contact)
    await message.answer(
        "Введите номер телефона или нажмите кнопку ниже 👇",
        reply_markup=contact_kb()
    )


@router.message(RegForm.contact)
async def finish(message: Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    contact = message.contact.phone_number if message.contact else message.text

    text = (
        "📥 Новая заявка\n\n"
        f"Имя: {data['name']}\n"
        f"Контакт: {contact}\n"
        f"Статус: {data['citizenship']}\n"
        f"Срок: {data['term']}\n"
        f"Срочность: {data['urgency']}"
    )

    await message.answer(
        "✅ Заявка отправлена. Мы свяжемся с вами.",
        reply_markup=remove_kb()
    )

    await message.bot.send_message(ADMIN_ID, text)
