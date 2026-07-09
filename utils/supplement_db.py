from utils.supabase_client import get_supabase_client
from utils.time_utils import now_bj_iso, format_bj_time, beijing_day_utc_range


def get_active_supplements():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplements")
        .select("*")
        .eq("is_active", True)
        .order("name", desc=False)
        .execute()
    )

    return result.data


def get_active_bottles_by_supplement(supplement_id):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplement_bottles")
        .select("*")
        .eq("supplement_id", supplement_id)
        .eq("status", "active")
        .order("created_at", desc=True)
        .execute()
    )

    return result.data

def calculate_bottle_remaining(bottle_id, initial_quantity):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplement_intakes")
        .select("amount")
        .eq("bottle_id", bottle_id)
        .execute()
    )

    used = sum(float(item["amount"] or 0) for item in result.data)
    initial = float(initial_quantity or 0)

    return max(initial - used, 0)


def get_person_by_name(name):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("people")
        .select("*")
        .eq("name", name)
        .limit(1)
        .execute()
    )

    return result.data[0] if result.data else None


def add_legacy_supplement_log(supplement_name, dosage, unit, note):
    supabase = get_supabase_client()
    now = now_bj_iso()

    return supabase.table("supplement_logs").insert({
        "supplement_name": supplement_name,
        "dosage": dosage,
        "unit": unit,
        "note": note,
        "taken_at": now,
        "created_at": now,
    }).execute()


def add_supplement_intake(person_name, supplement_id, bottle_id, amount, unit, notes):
    supabase = get_supabase_client()

    person = get_person_by_name(person_name)

    if not person:
        raise ValueError(f"Person not found: {person_name}")

    now = now_bj_iso()

    return supabase.table("supplement_intakes").insert({
        "person_id": person["id"],
        "supplement_id": supplement_id,
        "bottle_id": bottle_id,
        "taken_at": now,
        "amount": amount,
        "unit": unit,
        "notes": notes,
        "created_at": now,
    }).execute()


def delete_supplement_log(log_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplement_logs")
        .delete()
        .eq("id", log_id)
        .execute()
    )

def delete_supplement_intake(intake_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplement_intakes")
        .delete()
        .eq("id", intake_id)
        .execute()
    )

def get_supplement_logs_by_date(date):
    supabase = get_supabase_client()

    start_time, end_time = beijing_day_utc_range(date)

    result = (
        supabase
        .table("supplement_logs")
        .select("*")
        .gte("taken_at", start_time)
        .lt("taken_at", end_time)
        .order("taken_at", desc=True)
        .execute()
    )

    logs = []

    for row in result.data:
        logs.append({
            "id": row["id"],
            "supplement_name": row["supplement_name"],
            "dosage": row["dosage"],
            "unit": row["unit"],
            "note": row.get("note") or "",
            "taken_at": format_bj_time(row["taken_at"]),
            "created_at": format_bj_time(row["created_at"]),
        })

    return logs


def get_supplement_intakes_by_date(date):
    supabase = get_supabase_client()

    start_time, end_time = beijing_day_utc_range(date)

    result = (
        supabase
        .table("supplement_intakes")
        .select(
            """
            *,
            supplements(name),
            supplement_bottles(brand, product_name, strength, expiry_date)
            """
        )
        .gte("taken_at", start_time)
        .lt("taken_at", end_time)
        .order("taken_at", desc=True)
        .execute()
    )

    intakes = []

    for row in result.data:
        supplement = row.get("supplements") or {}
        bottle = row.get("supplement_bottles") or {}

        bottle_label_parts = [
            bottle.get("brand") or "",
            bottle.get("product_name") or "",
            bottle.get("strength") or "",
            f'exp {bottle.get("expiry_date")}' if bottle.get("expiry_date") else "",
        ]

        bottle_label = " | ".join([
            part for part in bottle_label_parts
            if part
        ])

        intakes.append({
            "id": row["id"],
            "supplement_name": supplement.get("name") or "",
            "bottle_label": bottle_label,
            "amount": row["amount"],
            "unit": row["unit"],
            "notes": row.get("notes") or "",
            "taken_at": format_bj_time(row["taken_at"]),
        })

    return intakes

def get_supplement_intake_daily_summary(date):
    intakes = get_supplement_intakes_by_date(date)

    summary_map = {}

    for intake in intakes:
        key = (intake["supplement_name"], intake["unit"])
        summary_map[key] = summary_map.get(key, 0) + float(intake["amount"] or 0)

    summary = []

    for (supplement_name, unit), total_amount in summary_map.items():
        summary.append({
            "supplement_name": supplement_name,
            "total_amount": total_amount,
            "unit": unit,
        })

    summary.sort(key=lambda x: x["supplement_name"])

    return summary

def get_supplement_daily_summary(date):
    logs = get_supplement_logs_by_date(date)

    summary_map = {}

    for log in logs:
        key = (log["supplement_name"], log["unit"])
        summary_map[key] = summary_map.get(key, 0) + float(log["dosage"] or 0)

    summary = []

    for (supplement_name, unit), total_dosage in summary_map.items():
        summary.append({
            "supplement_name": supplement_name,
            "total_dosage": total_dosage,
            "unit": unit,
        })

    summary.sort(key=lambda x: x["supplement_name"])

    return summary