from app.database import supabase
import pandas as pd
from app.config import KPI_TABLE, SUBMISSION_TABLE

SGT = "Asia/Singapore"

class SubmissionService:

    @staticmethod
    def create_submission(user_id, kpi_tag, message):
        kpi_id = (
            supabase.table(KPI_TABLE)
            .select("id")
            .eq("user_id", str(user_id))
            .eq("tag", str(kpi_tag).lower())
            .execute()
        ).data[0]["id"]

        if not kpi_id:
            return {"success": False, "error": "KPI not found"}

        return supabase.table(SUBMISSION_TABLE).insert({
            "kpi_id": kpi_id,
            "message": message
        }).execute()

    @staticmethod
    def get_today_submissions():
        today = pd.to_datetime("today").tz_localize(SGT).date()

        response = (
            supabase.table(SUBMISSION_TABLE)
            .select("*")
            .gte("created_at", str(today))
            .execute()
        )

        return response.data
