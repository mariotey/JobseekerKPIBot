"""
uv run python -m app.main
"""
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)

from app.config import BOT_TOKEN
from app.handlers import (
    add_kpi,
    list_kpis,
    detect_submission
)
from app.scheduler import setup_scheduler

# Store seen chat IDs in memory
seen_chats = set()

async def print_group_id(update, context):
    chat_id = update.effective_chat.id

    # only print ONCE per chat
    if chat_id not in seen_chats:
        print(f"GROUP ID: {chat_id}")
        seen_chats.add(chat_id)

app = ApplicationBuilder().token(BOT_TOKEN).build()

# Listen to ALL messages in group
app.add_handler(
    MessageHandler(filters.ALL, print_group_id)
)

# app.add_handler(CommandHandler("addkpi", add_kpi))
# app.add_handler(CommandHandler("kpi", list_kpis))
# app.add_handler(
#     MessageHandler(
#         filters.TEXT | filters.PHOTO,
#         detect_submission
#     )
# )

# def post_init(application):
#     setup_scheduler(application)

# app.post_init = post_init

if __name__ == "__main__":
    print("Bot started...")
    app.run_polling()