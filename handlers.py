from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import RegForm
from config import ADMIN_ID
from keyboards import (
    citizenship_kb,
    term_kb,
    urgency_kb,
    contact_kb,
    remove_kb,
    admin_lead_kb
)

router = Router()
LEAD_COUNTER = 0


@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegForm.citizenship)
    await message.answer(
        "👋 Здравствуйте!\n\n"
        "Помогаем с официальной временной регистрацией в Москве и МО.\n\n"
        "Выберите ваш статус:",
        reply_markup=citizenship_kb()
    )


@router.callback_query(RegForm.citizenship)
async def set_cit(cb: CallbackQuery, state: FSMContext):
    await state.update_data(citizenship=cb.data)
    await state.set_state(RegForm.term)
    await cb.message.edit_text(
        "На какой срок нужна регистрация?",
        reply_markup=term_kb()
    )


@router.callback_query(RegForm.term)
async def set_term(cb: CallbackQuery, state: FSMContext):
    prices = {
        "3m": "3 месяца — 6 000 ₽",
        "6m": "6 месяцев — 9 000 ₽",
        "12m": "12 месяцев — 12 000 ₽"
    }
    await state.update_data(term=prices.get(cb.data))
    await state.set_state(RegForm.urgency)
    await cb.message.edit_text(
        "Когда нужно оформить?",
        reply_markup=urgency_kb()
    )


@router.callback_query(RegForm.urgency)
async def set_urgency(cb: CallbackQuery, state: FSMContext):
    await state.update_data(urgency=cb.data)
    await state.set_state(RegForm.name)
    await cb.message.edit_text("Введите ваше имя:")


@router.message(RegForm.name)
async def set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegForm.contact)
    await message.answer(
        "Введите номер телефона или нажмите кнопку ниже 👇",
        reply_markup=contact_kb()
    )


@router.message(RegForm.contact)
async def finish_contact(message: Message, state: FSMContext):
    global LEAD_COUNTER

    data = await state.get_data()
    await state.clear()
    LEAD_COUNTER += 1

    contact_value = (
        message.contact.phone_number
        if message.contact
        else message.text
    )

    # 1️⃣ СНАЧАЛА СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЮ (ВСЕГДА)
    await message.answer(
        "✅ Заявка отправлена.\n\n"
        "Мы свяжемся с вами в ближайшее время.",
        reply_markup=remove_kb()
    )

    # 2️⃣ ПОТОМ АДМИНУ (ДАЖЕ ЕСЛИ ТУТ ОШИБКА — ПОЛЬЗОВАТЕЛЬ УЖЕ ОТВЕТ ПОЛУЧИЛ)
    try:
        text = (
            f"📥 *Новая заявка №{LEAD_COUNTER}*\n\n"
            f"👤 Имя: {data['name']}\n"
            f"📞 Контакт: {contact_value}\n"
            f"🪪 Статус: {data['citizenship']}\n"
            f"🗓 Срок: {data['term']}\n"
            f"⏱ Срочность: {data['urgency']}\n"
            f"👤 Telegram: @{message.from_user.username}"
        )

        await message.bot.send_message(
            ADMIN_ID,
            text,
            parse_mode="Markdown",
            reply_markup=admin_lead_kb(LEAD_COUNTER)
        )
    except Exception as e:
        print("ADMIN SEND ERROR:", e)
