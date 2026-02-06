from aiogram import Router, F
from aiogram.types import CallbackQuery
from config import ADMIN_ID

admin_router = Router()

@admin_router.callback_query(F.data.startswith(("work_", "fail_", "done_")))
async def lead_status(cb: CallbackQuery):
    if cb.from_user.id != ADMIN_ID:
        return

    statuses = {
        "work": "✅ Заявка принята в работу",
        "fail": "❌ К сожалению, мы не можем помочь по данному запросу",
        "done": "⭐ Заявка успешно закрыта"
    }

    action = cb.data.split("_")[0]

    await cb.answer("Статус обновлён")
    await cb.message.reply(statuses[action])
