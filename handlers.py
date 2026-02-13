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
    admin_menu_kb
)
from config import ADMIN_ID
from database import (
    add_lead,
    get_all_leads,
    get_today_stats,
    get_new_leads,
    update_lead_status,
    add_user,
    get_all_users
)

router = Router()
LEAD_COUNTER = 0


# ================= START =================

@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):

    # сохраняем пользователя
    username = (
        f"@{message.from_user.username}"
        if message.from_user.username
        else ""
    )
    add_user(message.from_user.id, username)

    await state.clear()
    await state.set_state(RegForm.citizenship)

    await message.answer(
        "📢 Перед началом рекомендуем ознакомиться с информацией "
        "в нашем Telegram-канале.\n"
        "Там вы найдёте ответы на частые вопросы и условия.",
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
        "📊 Чаще всего клиенты выбирают регистрацию на 6 месяцев —\n"
        "это самый удобный вариант по стоимости и сроку.\n\n"
        "Если нужна долгосрочная уверенность — выбирают год.\n\n"
        "Выберите подходящий вариант:",
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
        "📞 Оставьте номер телефона или нажмите кнопку ниже.\n"
        "Менеджер свяжется с вами в ближайшее время.",
        reply_markup=contact_kb()
    )


# ================= ФИНИШ =================


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

    lead_data = {
        "name": data["name"],
        "phone": contact,
        "telegram_id": message.from_user.id,
        "username": username,
        "citizenship": data["citizenship"],
        "term": data["term"],
        "urgency": data["urgency"]
    }

    add_lead(lead_data)

    # сообщение клиенту
    await message.answer(
        "✅ Заявка принята!\n\n"
        "Менеджер свяжется с вами в течение 5–15 минут.",
        reply_markup=remove_kb()
    )

    import asyncio

    await asyncio.sleep(3)

    await message.answer(
        "🔒 Работаем официально.\n\n"
        "Регистрация проходит через госорганы.\n"
        "Данные отображаются в базе при проверке."
    )

    await asyncio.sleep(4)

    await message.answer(
        "🤝 Никаких предоплат до консультации.\n\n"
        "Сначала менеджер разберёт вашу ситуацию "
        "и предложит подходящий вариант."
    )

    await asyncio.sleep(4)

    await message.answer(
        "📊 Чаще всего клиенты оформляют на 6 или 12 месяцев.\n\n"
        "Так выгоднее по стоимости и не нужно "
        "повторно заниматься продлением."
    )

    await asyncio.sleep(4)

    await message.answer(
        "☎️ Чтобы ускорить оформление, менеджер может уточнить:\n\n"
        "• адрес проживания\n"
        "• гражданство\n"
        "• когда нужна регистрация\n\n"
        "Можно заранее подготовить информацию 👍"
    )

    # сообщение админу
    admin_text = (
        f"📥 Новая заявка №{LEAD_COUNTER}\n\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {contact}\n"
        f"Telegram: {username}\n\n"
        f"Статус: {data['citizenship']}\n"
        f"Срок: {data['term']}\n"
        f"Срочность: {data['urgency']}"
    )

    await message.bot.send_message(
        ADMIN_ID,
        admin_text,
        reply_markup=admin_lead_kb(LEAD_COUNTER)
    )


# ================= СТАТУСЫ =================

@router.callback_query(F.data.startswith("lead_work_"))
async def lead_in_work(cb: CallbackQuery):
    lead_id = int(cb.data.split("_")[-1])
    update_lead_status(lead_id, "in_work")

    await cb.message.edit_reply_markup()
    await cb.message.reply("🟡 Статус заявки: В работе")
    await cb.answer()


@router.callback_query(F.data.startswith("lead_done_"))
async def lead_done(cb: CallbackQuery):
    lead_id = int(cb.data.split("_")[-1])
    update_lead_status(lead_id, "done")

    await cb.message.edit_reply_markup()
    await cb.message.reply("✅ Статус заявки: Закрыта")
    await cb.answer()


# ================= АДМИНКА =================

@router.message(F.text == "/admin")
async def admin_panel(message: Message):
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


# ================= ПОЛЬЗОВАТЕЛИ =================

@router.message(F.text == "👥 Пользователи")
async def users_list(message: Message):
    users = get_all_users()

    if not users:
        await message.answer("Пользователей нет")
        return

    text = "👥 Последние пользователи:\n\n"

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
