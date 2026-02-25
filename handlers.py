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
    admin_lead_kb,
    channel_kb,
    consent_kb
)

from config import ADMIN_ID
from database import (
    add_lead,
    get_all_leads,
    get_new_leads,
    update_lead_status,
    add_user,
    get_all_users_full,
    get_last_users,
    get_users_count
)

router = Router()

# ================= START =================

@router.message(Command("start"))
async def start(message: Message, state: FSMContext):
    username = f"@{message.from_user.username}" if message.from_user.username else ""
    add_user(message.from_user.id, username)

    await state.clear()
    await state.set_state(RegForm.citizenship)

    await message.answer(
        "Ознакомьтесь с информацией в нашем Telegram-канале.",
        reply_markup=channel_kb()
    )

    await message.answer("Выберите ваш статус:", reply_markup=citizenship_kb())


# ================= ВОРОНКА =================

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
        "Требуется согласие на обработку персональных данных.",
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
    await message.answer("Оставьте номер телефона:", reply_markup=contact_kb())


# ================= ФИНИШ =================

@router.message(RegForm.contact)
async def finish(message: Message, state: FSMContext):

    data = await state.get_data()
    await state.clear()

    contact = message.contact.phone_number if message.contact else message.text
    username = f"@{message.from_user.username}" if message.from_user.username else f"id:{message.from_user.id}"

    lead_id = add_lead({
        "name": data.get("name"),
        "phone": contact,
        "telegram_id": message.from_user.id,
        "username": username,
        "citizenship": data.get("citizenship"),
        "term": data.get("term"),
        "urgency": data.get("urgency")
    })

    client_number = random.randint(1000, 9999)

    await message.answer(
        f"Обращение зарегистрировано.\n\n"
        f"Номер дела: {client_number}\n\n"
        f"Специалист подключится в течение 5–15 минут.",
        reply_markup=remove_kb()
    )

    admin_text = (
        f"Заявка №{lead_id}\n\n"
        f"{data.get('name')}\n"
        f"{contact}\n"
        f"{username}\n\n"
        f"{data.get('citizenship')}\n"
        f"{data.get('term')}\n"
        f"{data.get('urgency')}"
    )

    await message.bot.send_message(
        ADMIN_ID,
        admin_text,
        reply_markup=admin_lead_kb(lead_id)
    )


# ================= DASHBOARD =================

@router.message(Command("admin"))
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return
    await send_admin_dashboard(message)


async def send_admin_dashboard(message: Message, edit=False):

    total_users = get_users_count()
    users = get_last_users()
    leads = get_all_leads()

    text = f"<b>Панель управления</b>\n\n"
    text += f"Пользователей: {total_users}\n\n"

    text += "<b>Последние пользователи:</b>\n"
    for telegram_id, username, first_seen in users:
        text += f"{first_seen} | {username if username else '—'}\n"

    text += "\n<b>Последние заявки:</b>\n"
    for lead in leads[:5]:
        text += f"№{lead[0]} | {lead[6]}\n"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh_dashboard")]
        ]
    )

    if edit:
        await message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


@router.callback_query(F.data == "refresh_dashboard")
async def refresh_dashboard(cb: CallbackQuery):
    await cb.answer()
    await send_admin_dashboard(cb.message, edit=True)


# ================= ОТВЕТ АДМИНА =================

@router.callback_query(F.data.startswith("reply_"))
async def reply_start(cb: CallbackQuery, state: FSMContext):
    await cb.answer()
    user_id = int(cb.data.replace("reply_", ""))
    await state.update_data(reply_user_id=user_id)
    await state.set_state(AdminReply.waiting_for_message)
    await cb.message.answer("Введите сообщение для пользователя:")


@router.message(AdminReply.waiting_for_message)
async def send_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get("reply_user_id")

    try:
        await message.bot.send_message(user_id, message.text)
        await message.answer("Сообщение отправлено.")
    except:
        await message.answer("Ошибка отправки.")

    await state.clear()


# ================= РАССЫЛКА =================

@router.message(Command("broadcast"))
async def broadcast_handler(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    text = message.text.replace("/broadcast", "").strip()
    if not text:
        await message.answer("Введите текст после команды.")
        return

    users = get_all_users_full()
    sent = 0
    failed = 0
    batch_size = 20

    await message.answer("Запуск рассылки...")

    for i in range(0, len(users), batch_size):
        batch = users[i:i + batch_size]

        for user in batch:
            try:
                await message.bot.send_message(user[0], text)
                sent += 1
            except TelegramRetryAfter as e:
                await asyncio.sleep(e.retry_after)
            except:
                failed += 1

        await asyncio.sleep(1.2)

    await message.answer(
        f"Рассылка завершена\n\n"
        f"Всего: {len(users)}\n"
        f"Отправлено: {sent}\n"
        f"Ошибок: {failed}"
    )
