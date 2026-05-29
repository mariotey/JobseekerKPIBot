from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
import pytz

from app.database import supabase
# from app.config import GROUP_ID
from app.services.kpi_service import KPIService

def build_report():
    failed = []
    in_progress = []

    kpis = (
        supabase.table("kpis")
        .select("*")
        .eq("deleted", False)
        .execute()
    )

    now = datetime.now(pytz.timezone("Asia/Singapore"))

    for kpi in kpis.data:
        progress = KPIService.get_progress(kpi)

        user = (
            supabase.table("users")
            .select("*")
            .eq("user_id", kpi["user_id"])
            .execute()
        ).data[0]

        username = user["username"]

        if kpi["frequency"] == "daily":
            if progress < kpi["target"]:
                failed.append(
                    f'- @{username} — {kpi["tag"]} ({progress}/{kpi["target"]})'
                )

        else:
            created = datetime.fromisoformat(kpi["created_at"])
            end = created + timedelta(days=7)

            if now >= end:
                if progress < kpi["target"]:
                    failed.append(
                        f'- @{username} — {kpi["tag"]} ({progress}/{kpi["target"]})'
                    )
            else:
                if progress < kpi["target"]:
                    in_progress.append(
                        f'- @{username} — {kpi["tag"]} ({progress}/{kpi["target"]})'
                    )

    report = "📊 DAILY KPI REPORT\n\n"

    report += "❌ Failed KPIs\n"

    if failed:
        report += "\n".join(failed)
    else:
        report += "None"

    report += "\n\n⏳ In Progress\n"

    if in_progress:
        report += "\n".join(in_progress)
    else:
        report += "None"

    return report


async def send_daily_report(application):
    report = build_report()

    await application.bot.send_message(
        chat_id=GROUP_ID,
        text=report
    )


def setup_scheduler(application):
    scheduler = AsyncIOScheduler(timezone="Asia/Singapore")

    scheduler.add_job(
        send_daily_report,
        trigger="cron",
        hour=23,
        minute=59,
        args=[application]
    )

    scheduler.start()