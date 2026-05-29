from telegram import Update
from telegram.ext import ContextTypes

from app.services.kpi_service import KPIService

HELP_TEXT = """
📌 Available Commands
/help - Show this help message
/addkpi - Add a new KPI
/viewkpi - View all KPIs
/deletekpi - Delete a KPI (only for the user who created it)

🟢 KPI Setup
/addkpi Title | 1 | daily | #tag

🟡 KPI Management
/deletekpi #tag

🔵 Usage
Just post messages with your KPI tag:
“I applied to Google #applyjob”

📊 Reports
Daily report is automatic at 23:59 SGT
"""

async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("'/help command received\n")

    if not update.message:
        return

    await update.message.reply_text(HELP_TEXT)

async def add_kpi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"'/addkpi command received\n")

    user = update.effective_user
    text = update.message.text

    try:
        raw = text.replace("/addkpi", "").strip()

        title, target, frequency, tag = [x.strip() for x in raw.split("|")]

        # validation
        if frequency not in ["daily", "weekly"]:
            await update.message.reply_text("Frequency must be daily or weekly")
            return

        if not tag.startswith("#"):
            await update.message.reply_text("Tag must start with #")
            return

        if " " in tag:
            await update.message.reply_text("Tag cannot contain spaces")
            return

        print("\n", user.id, user.username, title, target, frequency, tag, "\n")

        # Register User if not exists
        KPIService.register_user(user)

        # Create KPI
        create_kpi_msg = KPIService.create_kpi(
            user=user,
            title=title,
            target=int(target),
            frequency=frequency,
            tag=tag.lower()
        )

        await update.message.reply_text(create_kpi_msg)

    except ValueError:
        await update.message.reply_text(
            "Invalid format.\nUse:\n/addkpi Title | 1 | daily | #tag"
        )

    except Exception as e:
        await update.message.reply_text(
            f"Error creating KPI: {e.details}\n\nUse:\n/addkpi Title | 1 | daily | #tag"
        )
        print(e)


async def view_kpi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"'/viewkpi command received\n")

    kpis, user_map = KPIService.get_all_kpis()

    if not kpis:
        await update.message.reply_text("No KPIs found.")
        return

    grouped = {}

    for kpi in kpis:
        user_id = kpi["user_id"]
        username = user_map.get(user_id, user_id)

        grouped.setdefault(username, []).append(kpi)

    message = "📊 All Users KPIs\n\n"

    for user, user_kpis in grouped.items():
        message += f"@{user} ({len(user_kpis)} KPIs)\n"

        for idx, kpi in enumerate(user_kpis, 1):
            message += (
                f"{idx}. {kpi['title']} "
                f"({kpi['target']}/{kpi['frequency']}) "
                f"{kpi['tag']}\n"
            )

        message += "\n"

    await update.message.reply_text(message)


async def delete_kpi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"'/deletekpi command received\n")

    user = update.effective_user
    text = update.message.text

    try:
        tag = text.replace("/deletekpi", "").strip().lower()

        if not tag.startswith("#"):
            await update.message.reply_text("Tag must start with #")
            return

        result = KPIService.delete_kpi(str(user.id), tag)

        if not result["success"]:
            await update.message.reply_text(f"❌ KPI not found: {tag}")
            return

        kpi = result["data"]

        await update.message.reply_text(
            f"✅ KPI deleted: {tag} — {kpi['title']}"
        )

    except Exception as e:
        print(e)
        await update.message.reply_text("Error deleting KPI")