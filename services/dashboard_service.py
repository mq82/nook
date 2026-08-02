import pandas as pd

from utils.supabase_client import get_supabase_client
from services.supplement_service import enrich_bottle_with_remaining


def get_low_stock_supplement_bottles(threshold=10):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplement_bottles")
        .select("*, supplements(name)")
        .eq("status", "active")
        .execute()
    )

    low_stock = []

    for bottle in result.data:
        enriched = enrich_bottle_with_remaining(bottle)

        if enriched["remaining"] <= threshold:
            supplement = enriched.get("supplements") or {}

            low_stock.append({
                "supplement_name": supplement.get("name") or "",
                "brand": enriched.get("brand") or "",
                "product_name": enriched.get("product_name") or "",
                "remaining": enriched["remaining"],
                "unit": enriched.get("unit") or "",
            })

    return low_stock


def get_personal_dashboard(today):
    """
    Dashboard data for the Personal section.
    """

    supabase = get_supabase_client()

    # ---------- Ping Ping ----------

    plans_result = (
        supabase
        .table("supplement_plans")
        .select("*")
        .eq("is_active", True)
        .lte("start_date", today)
        .or_(f"end_date.is.null,end_date.gte.{today}")
        .execute()
    )

    active_plans = plans_result.data

    total_pingping = len(active_plans)

    active_plan_ids = {
        plan["id"]
        for plan in active_plans
    }

    checkins_result = (
        supabase
        .table("supplement_plan_checkins")
        .select("*")
        .eq("checkin_date", today)
        .eq("is_taken", True)
        .execute()
    )

    completed_pingping = len([
        item
        for item in checkins_result.data
        if item["plan_id"] in active_plan_ids
    ])

    # ---------- Vera ----------

    supplement_result = (
        supabase
        .table("supplement_logs")
        .select("*")
        .gte("taken_at", f"{today}T00:00:00+08:00")
        .lt("taken_at", f"{today}T23:59:59+08:00")
        .execute()
    )

    vera_logs = supplement_result.data

    return {
        "vera_logs": vera_logs,
        "completed_pingping": completed_pingping,
        "total_pingping": total_pingping,
        "low_stock": get_low_stock_supplement_bottles(),
    }



from utils.home_db import (
    get_meals_by_date,
    get_expiring_inventory_items,
    get_shopping_items,
    get_all_chores,
)


def get_home_dashboard(today):
    """
    Dashboard data for the Home section.
    """

    # ---------- Meals ----------

    meals_today = get_meals_by_date(today)

    # ---------- Inventory ----------

    expiring_items = get_expiring_inventory_items(days=3)

    expiring_items = sorted(
        expiring_items,
        key=lambda x: (
            x["days_until_expiry"],
            x["name"].lower(),
        ),
    )

    # ---------- Shopping ----------

    shopping_items = get_shopping_items()

    shopping_pending = [
        item
        for item in shopping_items
        if not item["is_purchased"]
    ]

    shopping_purchased = [
        item
        for item in shopping_items
        if item["is_purchased"]
    ]

    # ---------- Chores ----------

    chores = get_all_chores()

    todo_chores = [
        chore
        for chore in chores
        if not chore["completed"]
    ]

    completed_chores = [
        chore
        for chore in chores
        if chore["completed"]
    ]

    return {
        "meals_today": meals_today,
        "expiring_items": expiring_items,
        "shopping_pending": shopping_pending,
        "shopping_purchased": shopping_purchased,
        "todo_chores": todo_chores,
        "completed_chores": completed_chores,
    }



def get_lifestyle_dashboard(today, today_date):
    """
    Dashboard data for Lifestyle section.
    """

    supabase = get_supabase_client()

    # ---------- Kombucha ----------

    kombucha_result = (
        supabase
        .table("kombucha_batches")
        .select("*")
        .eq("status", "Active")
        .order("start_date", desc=False)
        .execute()
    )

    active_kombucha = kombucha_result.data

    oldest_kombucha_days = None
    oldest_kombucha_name = None

    if active_kombucha:

        oldest = active_kombucha[0]

        start = pd.to_datetime(
            oldest["start_date"]
        ).date()

        oldest_kombucha_days = (
            today_date - start
        ).days

        oldest_kombucha_name = oldest["batch_name"]

    # ---------- Ballet ----------

    ballet_result = (
        supabase
        .table("ballet_classes")
        .select("duration_hours")
        .execute()
    )

    ballet_hours = sum(
        item["duration_hours"]
        for item in ballet_result.data
    ) if ballet_result.data else 0

    current_month = today[:7]

    ballet_month_result = (
        supabase
        .table("ballet_classes")
        .select("*")
        .gte(
            "class_date",
            f"{current_month}-01",
        )
        .execute()
    )

    ballet_this_month_hours = sum(
        item["duration_hours"]
        for item in ballet_month_result.data
    ) if ballet_month_result.data else 0

    last_class_result = (
        supabase
        .table("ballet_classes")
        .select("*")
        .order(
            "class_date",
            desc=True,
        )
        .limit(1)
        .execute()
    )

    last_class = (
        last_class_result.data[0]
        if last_class_result.data
        else None
    )

    return {
        "active_kombucha": active_kombucha,
        "oldest_kombucha_days": oldest_kombucha_days,
        "oldest_kombucha_name": oldest_kombucha_name,
        "ballet_hours": ballet_hours,
        "ballet_this_month_hours": ballet_this_month_hours,
        "last_class": last_class,
    }


def get_period_dashboard(today, today_date):
    """
    Dashboard data for Period section.
    """

    supabase = get_supabase_client()

    # ---------- Latest Period ----------

    period_result = (
        supabase
        .table("cycle_periods")
        .select("*")
        .order("start_date", desc=True)
        .limit(1)
        .execute()
    )

    latest_period = (
        period_result.data[0]
        if period_result.data
        else None
    )

    cycle_day = None
    latest_period_start = None
    latest_period_end = None

    if latest_period:

        latest_period_start = pd.to_datetime(
            latest_period["start_date"]
        ).date()

        latest_period_end = (
            pd.to_datetime(
                latest_period["end_date"]
            ).date()
            if latest_period.get("end_date")
            else None
        )

        cycle_day = (
            today_date - latest_period_start
        ).days + 1

    # ---------- Prediction ----------

    predicted_next_period = None
    days_until_next_period = None

    period_history_result = (
        supabase
        .table("cycle_periods")
        .select("*")
        .order("start_date", desc=False)
        .execute()
    )

    history = period_history_result.data

    if len(history) >= 2 and latest_period_start:

        df = pd.DataFrame(history)

        df["start_date"] = pd.to_datetime(
            df["start_date"]
        )

        df = df.sort_values("start_date")

        df["cycle_length_days"] = (
            df["start_date"]
            .diff()
            .dt.days
        )

        recent = (
            df["cycle_length_days"]
            .dropna()
            .tail(6)
        )

        if not recent.empty:

            avg_cycle = int(
                round(recent.mean())
            )

            predicted_next_period = (
                latest_period_start
                + pd.Timedelta(days=avg_cycle)
            )

            days_until_next_period = (
                predicted_next_period
                - today_date
            ).days

    # ---------- Daily Log ----------

    daily_log_result = (
        supabase
        .table("daily_logs")
        .select("*")
        .eq("log_date", today)
        .limit(1)
        .execute()
    )

    today_daily_log = (
        daily_log_result.data[0]
        if daily_log_result.data
        else None
    )

    return {
        "cycle_day": cycle_day,
        "latest_period_start": latest_period_start,
        "latest_period_end": latest_period_end,
        "predicted_next_period": predicted_next_period,
        "days_until_next_period": days_until_next_period,
        "today_daily_log": today_daily_log,
    }