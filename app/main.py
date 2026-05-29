"""
python -m app.main
"""
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters
)
from app.config import BOT_TOKEN
from app.handlers import help_handler, add_kpi, view_kpi

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
    MessageHandler(filters.TEXT & ~filters.COMMAND, print_group_id)
)
app.add_handler(CommandHandler("help", help_handler))
app.add_handler(CommandHandler("addkpi", add_kpi))
app.add_handler(CommandHandler("viewkpi", view_kpi))

if __name__ == "__main__":
    print("Bot started...")
    app.run_polling()