from app.database import supabase
from app.config import USER_TABLE, KPI_TABLE, SUBMISSION_TABLE

class KPIService:
    @staticmethod
    def register_user(user):
        user_id = str(user.id)
        username = str(user.username)

        existing = supabase.table(USER_TABLE) \
            .select("*") \
            .eq("id", user_id) \
            .execute()

        if existing.data:
            print(f"User already exists, skipping registration: {user_id}\n")
            return

        supabase.table(USER_TABLE).insert({
            "id": user_id,
            "username": username
        }).execute()

        print(f"Registered new user: {user_id} - {username}\n")

    @staticmethod
    def create_kpi(user, title, target, frequency, tag):
        user_id = str(user.id)
        username = str(user.username)

        existing = (
            supabase.table(KPI_TABLE)
            .select("id")
            .eq("user_id", user_id)
            .eq("tag", tag)
            .execute()
        )

        if existing.data:
            msg = f"KPI tag already exists for {username}! Use another tag!\n"
            print(msg)
            return msg

        # insert KPI
        supabase.table(KPI_TABLE).insert({
            "user_id": user_id,
            "title": title,
            "target": target,
            "frequency": frequency,
            "tag": tag,
            "deleted": False
        }).execute()

        msg = f"🎯 KPI Created\n{tag} — {title} ({target}/{frequency})\n"

    @staticmethod
    def get_all_kpis():
        kpis = (
            supabase.table(KPI_TABLE)
            .select("*")
            .eq("deleted", False)
            .execute()
        ).data

        users = response = (
            supabase.table(USER_TABLE)
            .select("*")
            .execute()
        ).data

        user_map = {u["id"]: u.get("username", u["id"]) for u in users}

        return kpis, user_map

    @staticmethod
    def delete_kpi(user_id, tag):

        response = (
            supabase.table(KPI_TABLE)
            .update({"deleted": True})
            .eq("user_id", user_id)
            .eq("tag", tag)
            .eq("deleted", False)
            .execute()
        )

        if not response.data:
            return {
                "success": False,
                "message": "KPI not found"
            }

        return {
            "success": True,
            "data": response.data[0]
        }