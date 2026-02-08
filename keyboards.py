from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

CHANNEL_URL = "https://t.me/propiska_v_moskve_1"


def channel_kb():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📢 Наш Telegram-канал",
                    url=CHANNEL_URL
                )
            ]
        ]
    )


def citizenship_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🇷🇺 Гражданин РФ")],
            [KeyboardButton(text="🌍 СНГ")],
            [KeyboardButton(text="🇧🇾 Беларусь")]
        ],
        resize_keyboard=True
    )


def term_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="3 месяца — 8000 ₽")],
            [KeyboardButton(text="6 месяцев — 11000 ₽")],
            [KeyboardButton(text="12 месяцев — 15000 ₽")]
        ],
        resize_keyboard=True
    )


def urgency_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Срочно")],
            [KeyboardButton(text="В течение недели")],
            [KeyboardButton(text="Не срочно")]
        ],
        resize_keyboard=True
    )


def contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Поделиться контактом", request_contact=True)]
        ],
        resize_keyboard=True
    )


def remove_kb():
    return ReplyKeyboardRemove()


def admin_lead_kb(lead_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🟡 В работе",
                    callback_data=f"lead_work_{lead_id}"
                ),
                InlineKeyboardButton(
                    text="✅ Закрыта",
                    callback_data=f"lead_done_{lead_id}"
                )
            ]
        ]
    )
def admin_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🆕 Новые заявки")],
            [KeyboardButton(text="📋 Все заявки")],
            [KeyboardButton(text="📈 Сегодня")]
        ],
        resize_keyboard=True
    )
