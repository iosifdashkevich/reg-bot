from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

CHANNEL_URL = "https://t.me/propiska_v_moskve_1"


# ================= КАНАЛ =================

def channel_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🏛 Официальный информационный канал",
                    url=CHANNEL_URL
                )
            ]
        ]
    )


# ================= ГРАЖДАНСТВО =================

def citizenship_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Гражданин Российской Федерации")],
            [KeyboardButton(text="🌍 Граждане СНГ")],
            [KeyboardButton(text="🇧🇾 Республика Беларусь")]
        ],
        resize_keyboard=True
    )


# ================= ТАРИФЫ =================

def term_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="💼 1 месяц — 5 000 ₽")],
            [KeyboardButton(text="⭐ 6 месяцев — 11 000 ₽ • рекомендуемый")],
            [KeyboardButton(text="👑 12 месяцев — 15 000 ₽ • максимум защиты")],
            [KeyboardButton(text="📄 3 месяца — 8 000 ₽")]
        ],
        resize_keyboard=True
    )


# ================= СРОЧНОСТЬ =================

def urgency_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔥 Максимально срочно")],
            [KeyboardButton(text="📅 В плановом режиме")],
            [KeyboardButton(text="🕒 Без спешки")]
        ],
        resize_keyboard=True
    )


# ================= КОНТАКТ =================

def contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📲 Передать номер менеджеру", request_contact=True)]
        ],
        resize_keyboard=True
    )


# ================= УБРАТЬ =================

def remove_kb():
    return ReplyKeyboardRemove()


# ================= ДЛЯ МЕНЕДЖЕРА =================

def admin_lead_kb(lead_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟡 В работе",
                    callback_data=f"lead_work_{lead_id}"
                ),
                InlineKeyboardButton(
                    text="✅ Завершена",
                    callback_data=f"lead_done_{lead_id}"
                )
            ]
        ]
    )


# ================= АДМИН =================

def admin_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📋 Все заявки")],
            [KeyboardButton(text="🆕 Новые заявки")],
            [KeyboardButton(text="👥 Пользователи")]
        ],
        resize_keyboard=True
    )
