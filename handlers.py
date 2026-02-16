import random
import asyncio

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
    admin_lead_kb,
    channel_kb,
    admin_menu_kb,
    consent_kb
)
from config import ADMIN_ID
from database import (
    add_lead,
    get_all_leads,
    get_new_leads,
    update_lead_status,
    add_user,
    get_all_users
)

router = Router()


# ================= START =================

@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):

    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else ""
    )
    add_user(message.from_user.id, username)

    await state.clear()
    await state.set_state(RegForm.citizenship)

    await message.answer(
        "📢 Перед началом рекомендуем ознакомиться с информацией в нашем Telegram-канале.",
        reply_markup=channel_kb()
    )

    await message.answer(
        "Выберите ваш статус:",
        reply_markup=citizenship_kb()
    )


# ================= ВОРОНКА =================

@router.message(RegForm.citizenship)
async def step_citizenship(message: Message, state: FSMContext):
    clean_status = message.text.split(" ", 1)[-1]
    await state.update_data(citizenship=clean_status)

    await state.set_state(RegForm.term)
    await message.answer(
        "Выберите срок регистрации:",
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


# ================= СОГЛАСИЕ =================

@router.message(RegForm.urgency)
async def step_urgency(message: Message, state: FSMContext):
    await state.update_data(urgency=message.text)

    await state.set_state(RegForm.consent)
    await message.answer(
        "📄 Для продолжения требуется согласие на обработку персональных данных.\n\n"
        "Информация используется только для оформления и связи с вами.",
        reply_markup=consent_kb()
    )


@router.message(RegForm.consent)
async def step_consent(message: Message, state: FSMContext):

    if message.text == "❌ Не согласен":
        await message.answer("Без согласия продолжение невозможно.")
        return

    if message.text == "✅ Согласен":
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
        "📞 Оставьте номер телефона или нажмите кнопку ниже.",
        reply_markup=contact_kb()
    )


# ================= ФИНИШ =================

@router.message(RegForm.contact)
async def finish(message: Message, state: FSMContext):

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
        else f"id:{message.from_user.id}"
    )

    lead_data = {
        "name": data.get("name"),
        "phone": contact,
        "telegram_id": message.from_user.id,
        "username": username,
        "citizenship": data.get("citizenship"),
        "term": data.get("term"),
        "urgency": data.get("urgency")
    }

    lead_id = add_lead(lead_data)

    client_number = random.randint(1342, 1489)

    await message.answer(
    f"🏛 Обращение зарегистрировано в системе.\n\n"
    f"🧾 Номер вашего дела: {client_number}\n\n"
    f"📂 Материалы переданы на распределение специалисту.\n"
    f"👤 Ответственный сотрудник будет назначен автоматически.\n\n"
    f"💬 После назначения вам поступит персональное сообщение "
    f"в этом чате Telegram.\n\n"
    f"⏳ Среднее время подключения: 5–15 минут.\n\n"
    f"📌 Пожалуйста, оставайтесь на связи.",
    reply_markup=remove_kb()
)

    

    # уведомление админу
    admin_text = (
        f"📥 Заявка №{lead_id}\n\n"
        f"Имя: {data.get('name')}\n"
        f"Телефон: {contact}\n"
        f"Telegram: {username}\n\n"
        f"Статус: {data.get('citizenship')}\n"
        f"Срок: {data.get('term')}\n"
        f"Срочность: {data.get('urgency')}"
    )

    await message.bot.send_message(
        ADMIN_ID,
        admin_text,
        reply_markup=admin_lead_kb(lead_id)
    )

    # 🔥 ИМИТАЦИЯ НАЧАЛА РАБОТЫ
    await asyncio.sleep(90)

    await message.answer(
        "📂 По вашему обращению уже начата предварительная подготовка.\n\n"
        "Специалист скоро свяжется для уточнения деталей."
    )


# ================= СТАТУСЫ =================

@router.callback_query(F.data.startswith("lead_work_"))
async def lead_in_work(cb: CallbackQuery):
    await cb.answer()

    lead_raw = cb.data.replace("lead_work_", "")

    if not lead_raw.isdigit():
        await cb.message.answer("Ошибка номера заявки")
        return

    lead_id = int(lead_raw)

    update_lead_status(lead_id, "in_work")

    # ищем клиента
    leads = get_all_leads()
    client_id = None

    for lead in leads:
        if lead[0] == lead_id:
            client_id = lead[5]  # telegram_id
            break

    # убираем кнопки
    await cb.message.edit_reply_markup(reply_markup=None)

    # менеджеру
    await cb.message.answer(f"🟡 Заявка {lead_id} переведена в работу")

    # клиенту
    if client_id:
        try:
            await cb.bot.send_message(
                client_id,
                "👤 Ваше дело принято специалистом.\n\n"
                "📂 Начата подготовка документов.\n"
                "Сейчас проводится проверка данных для оформления.\n\n"
                "💬 В ближайшее время сотрудник напишет вам здесь.\n\n"
                "📌 Пожалуйста, оставайтесь на связи."
            )
        except Exception as e:
            print(f"Ошибка отправки клиенту: {e}")


@router.callback_query(F.data.startswith("lead_done_"))
async def lead_done(cb: CallbackQuery):
    await cb.answer()

    lead_raw = cb.data.replace("lead_done_", "")

    if not lead_raw.isdigit():
        await cb.message.answer("Ошибка номера заявки")
        return

    lead_id = int(lead_raw)

    update_lead_status(lead_id, "done")

    # ищем клиента
    leads = get_all_leads()
    client_id = None

    for lead in leads:
        if lead[0] == lead_id:
            client_id = lead[5]  # telegram_id
            break

    # убираем кнопки
    await cb.message.edit_reply_markup(reply_markup=None)

    # менеджеру
    await cb.message.answer(f"✅ Заявка {lead_id} закрыта")

    # клиенту
    if client_id:
        try:
            await cb.bot.send_message(
                client_id,
                "✅ Работа по вашему обращению завершена.\n\n"
                "Если потребуется помощь снова — будем рады помочь.\n"
                "Спасибо за доверие!"
            )
        except Exception as e:
            print(f"Ошибка отправки клиенту: {e}")


# ================= АДМИНКА =================

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    if message.from_user.id != ADMIN_ID:
        return

    await message.answer(
        "📊 Панель управления",
        reply_markup=admin_menu_kb()
    )


@router.message(F.text == "📋 Все заявки")
async def all_leads(message: Message):
    leads = get_all_leads()

    if not leads:
        await message.answer("Заявок нет")
        return

    text = "📋 Последние заявки:\n\n"

    for lead in leads:
        text += (
            f"№{lead[0]} | {lead[1]}\n"
            f"Имя: {lead[2]}\n"
            f"Телефон: {lead[3]}\n"
            f"Username: {lead[4]}\n"
            f"ID: {lead[5]}\n"
            f"Статус: {lead[6]}\n\n"
        )

    await message.answer(text)


@router.message(F.text == "🆕 Новые заявки")
async def new_leads(message: Message):
    leads = get_new_leads()

    if not leads:
        await message.answer("Новых заявок нет")
        return

    text = "🆕 Новые заявки:\n\n"

    for lead in leads:
        text += (
            f"№{lead[0]} | {lead[1]}\n"
            f"Имя: {lead[2]}\n"
            f"Телефон: {lead[3]}\n"
            f"Username: {lead[4]}\n"
            f"ID: {lead[5]}\n\n"
        )

    await message.answer(text)


@router.message(F.text == "👥 Пользователи")
async def users_list(message: Message):
    users = get_all_users()

    if not users:
        await message.answer("Пользователей нет")
        return

    text = "👥 Пользователи:\n\n"

    for user in users:
        tg_id, username, date = user
        if not username:
            username = "нет"

        text += (
            f"{date}\n"
            f"Username: {username}\n"
            f"ID: {tg_id}\n\n"
        )

    await message.answer(text)
