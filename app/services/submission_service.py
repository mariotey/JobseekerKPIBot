from app.database import supabase


class SubmissionService:

    @staticmethod
    def create_submission(user_id, kpi_id, message):
        return (
            supabase.table("submissions")
            .insert({
                "user_id": user_id,
                "kpi_id": kpi_id,
                "message": message
            })
            .execute()
        )