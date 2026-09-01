from utils.supabase_client import get_supabase_client


# ---------- Period Records ----------

def upsert_period_record(data):
    supabase = get_supabase_client()

    return (
        supabase
        .table("cycle_periods")
        .upsert(
            data,
            on_conflict="start_date",
        )
        .execute()
    )


def get_all_period_records():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("cycle_periods")
        .select("*")
        .order("start_date", desc=True)
        .execute()
    )

    return result.data


def update_period_record(
    record_id,
    data,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("cycle_periods")
        .update(data)
        .eq("id", record_id)
        .execute()
    )


def delete_period_record(
    record_id,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("cycle_periods")
        .delete()
        .eq("id", record_id)
        .execute()
    )


def upsert_period_records(records):
    supabase = get_supabase_client()

    return (
        supabase
        .table("cycle_periods")
        .upsert(
            records,
            on_conflict="start_date",
        )
        .execute()
    )


# ---------- Daily Logs ----------

def upsert_daily_log(data):
    supabase = get_supabase_client()

    return (
        supabase
        .table("daily_logs")
        .upsert(
            data,
            on_conflict="log_date",
        )
        .execute()
    )


def get_daily_logs(limit=30):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("daily_logs")
        .select("*")
        .order("log_date", desc=True)
        .limit(limit)
        .execute()
    )

    return result.data


def update_daily_log(
    log_id,
    data,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("daily_logs")
        .update(data)
        .eq("id", log_id)
        .execute()
    )


def delete_daily_log(
    log_id,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("daily_logs")
        .delete()
        .eq("id", log_id)
        .execute()
    )