from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

def start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Продолжить", callback_data="start")]
    ])

def citizenship_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇷🇺 Гражданин РФ", callback_data="cit_rf")],
        [InlineKeyboardButton(text="🌍 СНГ", callback_data="cit_sng")],
        [InlineKeyboardButton(text="🇧🇾 Беларусь", callback_data="cit_by")]
    ])

def term_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="3 месяца — 6 000 ₽", callback_data="3m")],
        [InlineKeyboardButton(text="6 месяцев — 9 000 ₽", callback_data="6m")],
        [InlineKeyboardButton(text="12 месяцев — 12 000 ₽", callback_data="12m")]
    ])

def urgency_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Срочно (1–3 дня)", callback_data="fast")],
        [InlineKeyboardButton(text="В течение недели", callback_data="week")],
        [InlineKeyboardButton(text="Не срочно", callback_data="free")]
    ])

def contact_kb():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📞 Поделиться контактом", request_contact=True)]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )

def remove_kb():
    return ReplyKeyboardRemove()

def admin_lead_kb(lead_id):
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ В работе", callback_data=f"work_{lead_id}"),
            InlineKeyboardButton(text="❌ Отказ", callback_data=f"fail_{lead_id}"),
            InlineKeyboardButton(text="⭐ Закрыта", callback_data=f"done_{lead_id}")
        ]
    ])
