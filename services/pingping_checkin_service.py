from datetime import datetime, timezone

from utils.supplement_db import (
    get_active_plans_by_date as db_get_active_plans_by_date,
    get_today_checkins as db_get_today_checkins,
    save_checkin as db_save_checkin,
)


def get_checkin_data(checkin_date):
    date_str = str(checkin_date)

    plans = db_get_active_plans_by_date(
        date_str
    )

    checkins = db_get_today_checkins(
        date_str
    )

    checkin_map = {
        item["plan_id"]: item
        for item in checkins
    }

    return {
        "plans": plans,
        "checkins": checkin_map,
    }


def save_plan_checkin(
    plan_id,
    checkin_date,
    is_taken,
):
    taken_at = (
        datetime.now(timezone.utc).isoformat()
        if is_taken
        else None
    )

    return db_save_checkin(
        plan_id=plan_id,
        checkin_date=str(checkin_date),
        is_taken=is_taken,
        taken_at=taken_at,
    )


def get_checkin_progress(
    plans,
    checkins,
):
    total = len(plans)

    completed = sum(
        1
        for plan in plans
        if (
            plan["id"] in checkins
            and checkins[plan["id"]]["is_taken"]
        )
    )

    progress = (
        completed / total
        if total
        else 0
    )

    return {
        "completed": completed,
        "total": total,
        "progress": progress,
    }


def get_checkin_rows(
    plans,
    checkins,
):
    rows = []

    for plan in plans:
        checkin = checkins.get(
            plan["id"]
        )

        rows.append({
            "timing": plan["timing"],
            "supplement_name": plan["supplement_name"],
            "dosage": plan["dosage"],
            "frequency": plan["frequency"],
            "taken": (
                checkin["is_taken"]
                if checkin
                else False
            ),
        })

    return rows