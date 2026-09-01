from utils.supabase_client import get_supabase_client
from utils.time_utils import now_bj_iso, format_bj_time, beijing_day_utc_range

# ---------- Supplements ----------

def get_all_supplements():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplements")
        .select("*")
        .order("name")
        .execute()
    )

    return result.data


def add_supplement(
    name,
    category,
    default_unit,
    description,
    notes,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplements")
        .insert({
            "name": name,
            "category": category,
            "default_unit": default_unit,
            "description": description,
            "notes": notes,
            "is_active": True,
        })
        .execute()
    )


def update_supplement(
    supplement_id,
    is_active,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplements")
        .update({
            "is_active": is_active,
        })
        .eq("id", supplement_id)
        .execute()
    )


def delete_supplement(
    supplement_id,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplements")
        .delete()
        .eq("id", supplement_id)
        .execute()
    )


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


# ---------- Supplement Bottles ----------

def get_all_bottles():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplement_bottles")
        .select("*, supplements(name)")
        .order("created_at", desc=True)
        .execute()
    )

    return result.data


def add_bottle(
    supplement_id,
    brand,
    product_name,
    strength,
    unit,
    quantity,
    purchase_date,
    expiry_date,
    opened_date,
    finished_date,
    purchase_place,
    price,
    lot_number,
    status,
    notes,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplement_bottles")
        .insert({
            "supplement_id": supplement_id,
            "brand": brand,
            "product_name": product_name,
            "strength": strength,
            "unit": unit,
            "quantity": quantity,
            "purchase_date": purchase_date,
            "expiry_date": expiry_date,
            "opened_date": opened_date,
            "finished_date": finished_date,
            "purchase_place": purchase_place,
            "price": price,
            "lot_number": lot_number,
            "status": status,
            "notes": notes,
        })
        .execute()
    )


def update_bottle(
    bottle_id,
    update_data,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplement_bottles")
        .update(update_data)
        .eq("id", bottle_id)
        .execute()
    )


def delete_bottle(
    bottle_id,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplement_bottles")
        .delete()
        .eq("id", bottle_id)
        .execute()
    )

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


# ---------- Supplement Plans ----------

def get_all_plans():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplement_plans")
        .select("""
            *,
            people(name),
            supplements(name),
            supplement_bottles(
                brand,
                product_name,
                strength,
                expiry_date
            )
        """)
        .order("start_date")
        .execute()
    )

    return result.data


def add_plan(
    person_id,
    supplement_id,
    bottle_id,
    supplement_name,
    dosage,
    frequency,
    timing,
    start_date,
    end_date,
    notes,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplement_plans")
        .insert({
            "person_id": person_id,
            "supplement_id": supplement_id,
            "bottle_id": bottle_id,
            "supplement_name": supplement_name,
            "dosage": dosage,
            "frequency": frequency,
            "timing": timing,
            "start_date": start_date,
            "end_date": end_date,
            "notes": notes,
            "is_active": True,
        })
        .execute()
    )


def update_plan(
    plan_id,
    update_data,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplement_plans")
        .update(update_data)
        .eq("id", plan_id)
        .execute()
    )


def delete_plan(
    plan_id,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplement_plans")
        .delete()
        .eq("id", plan_id)
        .execute()
    )


def get_active_plans_by_date(plan_date):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplement_plans")
        .select("*")
        .eq("is_active", True)
        .lte("start_date", plan_date)
        .or_(
            f"end_date.is.null,end_date.gte.{plan_date}"
        )
        .order("timing", desc=False)
        .execute()
    )

    return result.data

# ---------- Supplement Checkins ----------

def get_today_checkins(checkin_date):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("supplement_plan_checkins")
        .select("*")
        .eq("checkin_date", checkin_date)
        .execute()
    )

    return result.data


def save_checkin(
    plan_id,
    checkin_date,
    is_taken,
    taken_at,
):
    supabase = get_supabase_client()

    existing = (
        supabase
        .table("supplement_plan_checkins")
        .select("id")
        .eq("plan_id", plan_id)
        .eq("checkin_date", checkin_date)
        .execute()
    )

    update_data = {
        "is_taken": is_taken,
        "taken_at": taken_at,
    }

    if existing.data:
        return (
            supabase
            .table("supplement_plan_checkins")
            .update(update_data)
            .eq("id", existing.data[0]["id"])
            .execute()
        )

    return (
        supabase
        .table("supplement_plan_checkins")
        .insert({
            "plan_id": plan_id,
            "checkin_date": checkin_date,
            "is_taken": is_taken,
            "taken_at": taken_at,
        })
        .execute()
    )


# ---------- Supplement Tracking ----------

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


def delete_supplement_intake(intake_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplement_intakes")
        .delete()
        .eq("id", intake_id)
        .execute()
    )


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


# ---------- Legacy Logs ----------

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


def delete_supplement_log(log_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("supplement_logs")
        .delete()
        .eq("id", log_id)
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