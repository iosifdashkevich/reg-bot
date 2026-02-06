from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from states import RegForm
from keyboards import (
    citizenship_kb,
    term_kb,
    urgency_kb,
    contact_kb,
    remove_kb,
    admin_lead_kb
)
from config import ADMIN_ID

router = Router()
LEAD_COUNTER = 0


@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(RegForm.citizenship)

    await message.answer(
        "👋 Здравствуйте!\n\n"
        "Мы помогаем с *официальной временной регистрацией* в Москве и МО.\n\n"
        "✔️ реальные адреса\n"
        "✔️ оформление через госорганы\n"
        "✔️ сопровождение на весь срок\n\n"
        "Ответьте на несколько вопросов — подберём оптимальный вариант 👇",
        parse_mode="Markdown",
        reply_markup=citizenship_kb()
    )


@router.message(RegForm.citizenship)
async def step_citizenship(message: Message, state: FSMContext):
    clean_status = message.text.split(" ", 1)[-1]
    await state.update_data(citizenship=clean_status)

    await state.set_state(RegForm.term)
    await message.answer(
        "На какой срок нужна регистрация?",
        reply_markup=term_kb()
    )


@router.message(RegForm.term)
async def step_term(message: Message, state: FSMContext):
    await state.update_data(term=message.text)

    await state.set_state(RegForm.urgency)
    await message.answer(
        "Когда нужно оформить?",
        reply_markup=urgency_kb()
    )


@router.message(RegForm.urgency)
async def step_urgency(message: Message, state: FSMContext):
    await state.update_data(urgency=message.text)

    await state.set_state(RegForm.name)
    await message.answer(
        "Как к вам можно обращаться?",
        reply_markup=remove_kb()
    )


@router.message(RegForm.name)
async def step_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)

    await state.set_state(RegForm.contact)
    await message.answer(
        "📞 Оставьте номер телефона или нажмите кнопку ниже.\n\n"
        "Менеджер свяжется с вами в ближайшее время.",
        reply_markup=contact_kb()
    )


@router.message(RegForm.contact)
async def finish(message: Message, state: FSMContext):
    global LEAD_COUNTER
    LEAD_COUNTER += 1

    data = await state.get_data()
    await state.clear()

    contact = (
        message.contact.phone_number
        if message.contact
        else message.text
    )

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else f"tg://user?id={message.from_user.id}"
    )

    # 🧑‍💼 Сообщение клиенту
    await message.answer(
        "✅ *Заявка принята!*\n\n"
        "Наш менеджер свяжется с вами в течение *5–15 минут*.\n\n"
        "Если потребуется срочно — просто напишите в этот чат.",
        parse_mode="Markdown",
        reply_markup=remove_kb()
    )

    # 📥 Красивая заявка админу
    admin_text = (
        f"📥 *Новая заявка №{LEAD_COUNTER}*\n\n"
        f"👤 Имя: {data['name']}\n"
        f"📞 Телефон: {contact}\n"
        f"👤 Telegram: {username}\n\n"
        f"🪪 Статус: {data['citizenship']}\n"
        f"🗓 Срок: {data['term']}\n"
        f"⏱ Срочность: {data['urgency']}"
    )

    await message.bot.send_message(
        ADMIN_ID,
        admin_text,
        parse_mode="Markdown",
        reply_markup=admin_lead_kb(LEAD_COUNTER)
    )


# ───────── АДМИН-КНОПКИ ─────────
@router.callback_query(F.data.startswith("lead_work_"))
async def lead_in_work(cb: CallbackQuery):
    await cb.message.edit_reply_markup()
    await cb.message.reply("🟡 Статус заявки: *В работе*", parse_mode="Markdown")
    await cb.answer()


@router.callback_query(F.data.startswith("lead_done_"))
async def lead_done(cb: CallbackQuery):
    await cb.message.edit_reply_markup()
    await cb.message.reply("✅ Статус заявки: *Закрыта*", parse_mode="Markdown")
    await cb.answer()
