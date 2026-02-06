from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import RegForm
from keyboards import (
    start_kb,
    citizenship_kb,
    term_kb,
    urgency_kb,
    admin_lead_kb
)
from config import ADMIN_ID

router = Router()

LEAD_COUNTER = 0


# ─────────────── START ───────────────
@router.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "👋 Здравствуйте!\n\n"
        "Помогаем с официальной временной регистрацией в Москве и МО.\n\n"
        "✔️ реальные адреса\n"
        "✔️ оформление через госорганы\n"
        "✔️ сопровождение на весь срок\n\n"
        "Ответьте на пару вопросов — подберём вариант.",
        reply_markup=start_kb()
    )


# ─────────────── START FORM ───────────────
@router.callback_query(F.data == "start")
async def start_form(cb: CallbackQuery, state: FSMContext):
    await state.set_state(RegForm.citizenship)
    await cb.message.edit_text(
        "Выберите ваш статус:",
        reply_markup=citizenship_kb()
    )


# ─────────────── CITIZENSHIP ───────────────
@router.callback_query(RegForm.citizenship)
async def set_cit(cb: CallbackQuery, state: FSMContext):
    await state.update_data(citizenship=cb.data)
    await state.set_state(RegForm.term)
    await cb.message.edit_text(
        "На какой срок нужна регистрация?",
        reply_markup=term_kb()
    )


# ─────────────── TERM ───────────────
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


# ─────────────── URGENCY ───────────────
@router.callback_query(RegForm.urgency)
async def set_urgency(cb: CallbackQuery, state: FSMContext):
    await state.update_data(urgency=cb.data)
    await state.set_state(RegForm.name)
    await cb.message.edit_text(
        "🔒 Регистрация оформляется официально, с внесением в базу.\n\n"
        "Введите ваше имя:"
    )


# ─────────────── NAME ───────────────
@router.message(RegForm.name)
async def set_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegForm.contact)
    await message.answer(
        "Введите номер телефона или нажмите кнопку ниже 👇",
        reply_markup=contact_kb()
    )


# ─────────────── CONTACT (TEXT OR CONTACT) ───────────────
@router.message(RegForm.contact)
async def finish_contact(message: Message, state: FSMContext):
    global LEAD_COUNTER

    data = await state.get_data()
    await state.clear()
    LEAD_COUNTER += 1

    if message.contact:
        contact_value = message.contact.phone_number
    else:
        contact_value = message.text

    text = (
        f"📥 *Новая заявка №{LEAD_COUNTER}*\n\n"
        f"👤 Имя: {data.get('name')}\n"
        f"📞 Контакт: {contact_value}\n"
        f"🪪 Статус: {data.get('citizenship')}\n"
        f"🗓 Срок: {data.get('term')}\n"
        f"⏱ Срочность: {data.get('urgency')}\n"
        f"👤 Telegram: @{message.from_user.username}"
    )

    await message.bot.send_message(
        ADMIN_ID,
        text,
        parse_mode="Markdown",
        reply_markup=admin_lead_kb(LEAD_COUNTER)
    )

    await message.answer(
        "✅ Заявка отправлена.\n\n"
        "Мы свяжемся с вами в ближайшее время.",
        reply_markup=remove_kb()
    )
