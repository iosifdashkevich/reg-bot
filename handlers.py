import random
import asyncio

from aiogram import Router, F
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.exceptions import TelegramRetryAfter

from states import RegForm, AdminReply
from keyboards import (
    citizenship_kb,
    term_kb,
    urgency_kb,
    contact_kb,
    remove_kb,
    channel_kb,
    consent_kb
)

from config import ADMIN_ID
from database import (
    add_lead,
    update_lead_status,
    add_user,
    get_all_users_full,
    get_users_count,
    get_last_users,
    get_lead_by_id,
    get_all_leads
)

router = Router()

# =====================================================
# START
# =====================================================

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    username = f"@{message.from_user.username}" if message.from_user.username else ""
    add_user(message.from_user.id, username)

    await state.clear()
    await state.set_state(RegForm.citizenship)

    await message.answer(
        "📢 Ознакомьтесь с информацией в нашем Telegram-канале.",
        reply_markup=channel_kb()
    )
    await message.answer("Выберите ваш статус:", reply_markup=citizenship_kb())


# =====================================================
# ВОРОНКА
# =====================================================

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
    await state.set_state(RegForm.consent)
    await message.answer(
        "📄 Требуется согласие на обработку персональных данных.",
        reply_markup=consent_kb()
    )


@router.message(RegForm.consent)
async def step_consent(message: Message, state: FSMContext):
    if message.text != "✅ Согласен":
        await message.answer("Без согласия продолжение невозможно.")
        return

    await state.set_state(RegForm.name)
    await message.answer("Как к вам можно обращаться?", reply_markup=remove_kb())


@router.message(RegForm.name)
async def step_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(RegForm.contact)
    await message.answer(
        "📞 Оставьте номер телефона или нажмите кнопку ниже.",
        reply_markup=contact_kb()
    )


# =====================================================
# СОЗДАНИЕ ЗАЯВКИ
# =====================================================

@router.message(RegForm.contact)
async def finish(message: Message, state: FSMContext):

    data = await state.get_data()
    await state.clear()

    contact = message.contact.phone_number if message.contact else message.text
    username = f"@{message.from_user.username}" if message.from_user.username else "без username"

    lead_id = add_lead({
        "name": data.get("name"),
        "phone": contact,
        "telegram_id": message.from_user.id,
        "username": username,
        "citizenship": data.get("citizenship"),
        "term": data.get("term"),
        "urgency": data.get("urgency")
    })

    await message.answer(
        "🏛 Обращение зарегистрировано.\n\n"
        "⏳ Специалист свяжется с вами в ближайшее время.",
        reply_markup=remove_kb()
    )

    admin_text = (
        f"📥 <b>Новая заявка №{lead_id}</b>\n\n"
        f"👤 {data.get('name')}\n"
        f"📞 {contact}\n"
        f"🆔 {message.from_user.id}\n"
        f"🔗 {username}\n\n"
        f"Статус: new"
    )

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🟡 В работу", callback_data=f"inwork:{lead_id}"),
                InlineKeyboardButton(text="✅ Закрыть", callback_data=f"done:{lead_id}")
            ],
            [
                InlineKeyboardButton(text="✍ Ответить", callback_data=f"reply:{message.from_user.id}")
            ]
        ]
    )

    await message.bot.send_message(
        ADMIN_ID,
        admin_text,
        parse_mode="HTML",
        reply_markup=keyboard
    )


# =====================================================
# СТАТУС В РАБОТЕ
# =====================================================

@router.callback_query(F.data.startswith("inwork:"))
async def set_inwork(cb: CallbackQuery):
    await cb.answer()

    lead_id = int(cb.data.split(":")[1])
    update_lead_status(lead_id, "in_work")

    client_id = get_lead_by_id(lead_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✍ Ответить",
                    callback_data=f"reply:{client_id}"
                )
            ]
        ]
    )

    await cb.message.edit_reply_markup(reply_markup=keyboard)

    if client_id:
        await cb.bot.send_message(
            client_id,
            "🏛 Обращение принято к исполнению.\n\n"
            "📂 Назначен специалист.\n"
            "📌 Он свяжется с вами в ближайшее время."
        )


# =====================================================
# СТАТУС ЗАКРЫТА
# =====================================================

@router.callback_query(F.data.startswith("done:"))
async def set_done(cb: CallbackQuery):
    await cb.answer()

    lead_id = int(cb.data.split(":")[1])
    update_lead_status(lead_id, "done")

    await cb.message.edit_reply_markup(reply_markup=None)

    client_id = get_lead_by_id(lead_id)

    if client_id:
        await cb.bot.send_message(
            client_id,
            "✅ Работа по вашему обращению завершена.\n\n"
            "Если потребуется помощь — будем рады помочь снова."
        )


# =====================================================
# ОТВЕТ АДМИНА
# =====================================================

@router.callback_query(F.data.startswith("reply:"))
async def reply_start(cb: CallbackQuery, state: FSMContext):
    await cb.answer()

    user_id = int(cb.data.split(":")[1])
    await state.update_data(reply_user_id=user_id)
    await state.set_state(AdminReply.waiting_for_message)

    await cb.message.answer("✍ Введите сообщение для пользователя:")


@router.message(AdminReply.waiting_for_message)
async def send_reply(message: Message, state: FSMContext):

    data = await state.get_data()
    user_id = data.get("reply_user_id")

    try:
        await message.bot.send_message(user_id, message.text)
        await message.answer("✅ Сообщение отправлено пользователю.")
    except:
        await message.answer("❌ Ошибка отправки.")

    await state.clear()


# =====================================================
# DASHBOARD
# =====================================================

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    total_users = get_users_count()
    leads = get_all_leads()

    text = f"<b>📊 Панель управления</b>\n\n"
    text += f"👥 Пользователей: {total_users}\n\n"
    text += "<b>Последние заявки:</b>\n"

    keyboard = []

    for lead in leads[:5]:
        lead_id = lead[0]
        status = lead[6]
        text += f"№{lead_id} | {status}\n"

        keyboard.append([
            InlineKeyboardButton(text="🟡", callback_data=f"inwork:{lead_id}"),
            InlineKeyboardButton(text="✅", callback_data=f"done:{lead_id}")
        ])

    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)

    await message.answer(text, parse_mode="HTML", reply_markup=markup)
