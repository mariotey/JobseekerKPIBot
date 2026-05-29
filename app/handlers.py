from telegram import Update
from telegram.ext import ContextTypes

from app.services.kpi_service import KPIService
from app.services.submission_service import SubmissionService
from app.utils.parser import extract_tag


async def add_kpi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    KPIService.register_user(user.id, user.username)

    try:
        raw = update.message.text.replace("/addkpi ", "")

        title, target, frequency, tag = [x.strip() for x in raw.split("|")]

        KPIService.create_kpi(
            user.id,
            title,
            int(target),
            frequency,
            tag
        )

        await update.message.reply_text(
            f"🎯 KPI Created\n{tag} — {title} ({target}/{frequency})"
        )

    except Exception:
        await update.message.reply_text(
            "Invalid format. Use: /addkpi Title | 1 | daily | #tag"
        )


async def list_kpis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    result = KPIService.get_user_kpis(user.id)

    if not result.data:
        await update.message.reply_text("No KPIs found.")
        return

    lines = []

    for kpi in result.data:
        progress = KPIService.get_progress(kpi)

        cycle = "today" if kpi["frequency"] == "daily" else "this cycle"

        lines.append(
            f'{kpi["tag"]} — {kpi["title"]} ({progress}/{kpi["target"]} {cycle})'
        )

    await update.message.reply_text("\n".join(lines))


async def detect_submission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_chat.id)

    user = update.effective_user

    message = update.message.caption or update.message.text

    tag = extract_tag(message)

    if not tag:
        return

    KPIService.register_user(user.id, user.username)

    kpi = KPIService.get_kpi_by_tag(user.id, tag)

    if not kpi:
        return

    SubmissionService.create_submission(
        user.id,
        kpi["id"],
        message
    )

    progress = KPIService.get_progress(kpi)

    completed = progress >= kpi["target"]

    status = "🎯 Completed" if completed else ""

    await update.message.reply_text(
        f"✔ @{user.username} — {tag} ({progress}/{kpi['target']}) {status}"
    )
