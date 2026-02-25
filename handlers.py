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
        f"🏛 Обращение зарегистрировано\n\n"
        f"⏳ Специалист свяжется с вами в ближайшее время.",
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
# КНОПКИ СТАТУСА В КАРТОЧКЕ
# =====================================================

@router.callback_query(F.data.startswith("inwork:"))
async def set_inwork(cb: CallbackQuery):
    await cb.answer()
    lead_id = int(cb.data.split(":")[1])

    update_lead_status(lead_id, "in_work")
    await cb.message.edit_reply_markup(reply_markup=None)

    client_id = get_lead_by_id(lead_id)

    if client_id:
        await cb.bot.send_message(
            client_id,
            "🏛 Обращение принято к исполнению.\n\n"
            "📂 Назначен ответственный специалист.\n"
            "🔎 Запущена процедура обработки.\n\n"
            "📌 Специалист свяжется с вами в ближайшее время."
        )


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
