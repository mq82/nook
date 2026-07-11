from utils.supabase_client import get_supabase_client
from utils.time_utils import now_bj_iso, format_bj_time

# home - meals
def add_meal(meal_date, meal_type, content):
    supabase = get_supabase_client()

    return supabase.table("meals").insert({
        "meal_date": meal_date,
        "meal_type": meal_type,
        "content": content,
        "created_at": now_bj_iso(),
    }).execute()


def get_meals_by_date(meal_date):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("meals")
        .select("*")
        .eq("meal_date", meal_date)
        .order("id", desc=True)
        .execute()
    )

    return [
        {
            "id": row["id"],
            "meal_date": row["meal_date"],
            "meal_type": row["meal_type"],
            "content": row["content"],
            "created_at": format_bj_time(row["created_at"]),
        }
        for row in result.data
    ]

def delete_meal(meal_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("meals")
        .delete()
        .eq("id", meal_id)
        .execute()
    )

# home - chores
def add_chore(title):
    supabase = get_supabase_client()

    return supabase.table("chores").insert({
        "title": title,
        "created_at": now_bj_iso(),
        "completed": False,
        "completed_by": None,
        "completed_at": None,
    }).execute()


def get_all_chores():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("chores")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    return [
        {
            "id": row["id"],
            "title": row["title"],
            "created_at": format_bj_time(row["created_at"]),
            "completed": bool(row["completed"]),
            "completed_by": row["completed_by"] or "",
            "completed_at": format_bj_time(row["completed_at"]),
        }
        for row in result.data
    ]


def complete_chore(chore_id, user_name):
    supabase = get_supabase_client()

    return (
        supabase
        .table("chores")
        .update({
            "completed": True,
            "completed_by": user_name,
            "completed_at": now_bj_iso(),
        })
        .eq("id", int(chore_id))
        .execute()
    )


def undo_chore(chore_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("chores")
        .update({
            "completed": False,
            "completed_by": None,
            "completed_at": None,
        })
        .eq("id", int(chore_id))
        .execute()
    )

def delete_chore(chore_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("chores")
        .delete()
        .eq("id", int(chore_id))
        .execute()
    )


# home - fridge inventory
def add_inventory_item(name, category, location, quantity, unit, purchase_date, expiry_date, notes):
    supabase = get_supabase_client()

    return supabase.table("inventory").insert({
        "name": name,
        "category": category,
        "location": location,
        "quantity": quantity,
        "unit": unit,
        "purchase_date": purchase_date,
        "expiry_date": expiry_date,
        "notes": notes,
        "created_at": now_bj_iso(),
    }).execute()


def get_inventory_items():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("inventory")
        .select("*")
        .order("id", desc=True)
        .execute()
    )

    return result.data

from datetime import date


def get_expiring_inventory_items(days=3):
    supabase = get_supabase_client()

    result = (
        supabase
        .table("inventory")
        .select("*")
        .not_.is_("expiry_date", "null")
        .order("expiry_date", desc=False)
        .execute()
    )

    today = date.today()
    items = []

    for row in result.data:
        expiry = row.get("expiry_date")
        if not expiry:
            continue

        expiry_date = date.fromisoformat(expiry)
        days_left = (expiry_date - today).days

        if days_left <= days:
            row["days_until_expiry"] = days_left
            items.append(row)

    return items

def delete_inventory_item(item_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("inventory")
        .delete()
        .eq("id", int(item_id))
        .execute()
    )

# personal daily - vera supplements
from utils.time_utils import beijing_day_utc_range