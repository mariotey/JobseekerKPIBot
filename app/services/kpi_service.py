from datetime import datetime, timedelta
from app.database import supabase


class KPIService:

    @staticmethod
    def register_user(
        user_id: int,
        username: str
    ):
        existing = (
            supabase.table("users")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )

        if existing.data:
            return

        supabase.table("users").insert({
            "user_id": user_id,
            "username": username
        }).execute()

    @staticmethod
    def create_kpi(
        user_id,
        title,
        target,
        frequency,
        tag
    ):
        return (
            supabase.table("kpis")
            .insert({
                "user_id": user_id,
                "title": title,
                "target": target,
                "frequency": frequency,
                "tag": tag.lower()
            })
            .execute()
        )

    @staticmethod
    def get_user_kpis(
        user_id
    ):
        return (
            supabase.table("kpis")
            .select("*")
            .eq("user_id", user_id)
            .eq("deleted", False)
            .execute()
        )

    @staticmethod
    def get_kpi_by_tag(
        user_id,
        tag
    ):
        result = (
            supabase.table("kpis")
            .select("*")
            .eq("user_id", user_id)
            .eq("tag", tag)
            .eq("deleted", False)
            .execute()
        )

        if not result.data:
            return None

        return result.data[0]

    @staticmethod
    def get_progress(
        kpi
    ):
        now = datetime.now()

        if kpi["frequency"] == "daily":
            start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            start = datetime.fromisoformat(kpi["created_at"])
            end = start + timedelta(days=7)

            while end < now:
                start = end
                end = start + timedelta(days=7)

        result = (
            supabase.table("submissions")
            .select("*")
            .eq("kpi_id", kpi["id"])
            .gte("created_at", start.isoformat())
            .execute()
        )

        return min(len(result.data), kpi["target"])
