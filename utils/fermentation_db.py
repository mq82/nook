from utils.supabase_client import get_supabase_client


# ---------- Kombucha ----------

def add_kombucha_batch(
    batch_name,
    start_date,
    tea_type,
    sugar_grams,
    liquid_ml,
    starter_description,
    status,
    notes,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("kombucha_batches")
        .insert({
            "batch_name": batch_name,
            "start_date": start_date,
            "tea_type": tea_type,
            "sugar_grams": sugar_grams,
            "liquid_ml": liquid_ml,
            "starter_description": starter_description,
            "status": status,
            "notes": notes,
        })
        .execute()
    )


def get_all_kombucha_batches():
    supabase = get_supabase_client()

    result = (
        supabase
        .table("kombucha_batches")
        .select("*")
        .order("start_date", desc=True)
        .execute()
    )

    return result.data


def update_kombucha_status(
    batch_id,
    status,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("kombucha_batches")
        .update({
            "status": status,
        })
        .eq("id", batch_id)
        .execute()
    )


# ---------- Pickles ----------

def add_pickle_batch(
    batch_name,
    start_date,
    ingredient,
    ingredient_weight_g,
    salt_g,
    water_ml,
    salt_percentage,
    salt_percentage_basis,
    method,
    notes,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("pickle_batches")
        .insert({
            "batch_name": batch_name,
            "start_date": start_date,
            "ingredient": ingredient,
            "ingredient_weight_g": ingredient_weight_g,
            "salt_g": salt_g,
            "water_ml": water_ml,
            "salt_percentage": salt_percentage,
            "salt_percentage_basis": salt_percentage_basis,
            "method": method,
            "status": "Active",
            "notes": notes,
        })
        .execute()
    )


def get_all_pickle_batches():
    supabase = get_supabase_client()

    response = (
        supabase
        .table("pickle_batches")
        .select("*")
        .order("start_date", desc=True)
        .execute()
    )

    return response.data or []


def update_pickle_status(batch_id, status):
    supabase = get_supabase_client()

    return (
        supabase
        .table("pickle_batches")
        .update({
            "status": status,
        })
        .eq("id", batch_id)
        .execute()
    )


def delete_pickle_batch(batch_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("pickle_batches")
        .delete()
        .eq("id", batch_id)
        .execute()
    )

# ---------- Yogurt ----------

def add_yogurt_batch(
    batch_name,
    start_date,
    start_time,
    milk_type,
    milk_volume_ml,
    starter_type,
    starter_amount,
    incubation_temperature_c,
    incubation_hours,
    strained,
    yield_ml,
    notes,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("yogurt_batches")
        .insert({
            "batch_name": batch_name,
            "start_date": start_date,
            "start_time": start_time,
            "milk_type": milk_type,
            "milk_volume_ml": milk_volume_ml,
            "starter_type": starter_type,
            "starter_amount": starter_amount,
            "incubation_temperature_c": incubation_temperature_c,
            "incubation_hours": incubation_hours,
            "strained": strained,
            "yield_ml": yield_ml,
            "status": "Active",
            "notes": notes,
        })
        .execute()
    )


def get_all_yogurt_batches():
    supabase = get_supabase_client()

    response = (
        supabase
        .table("yogurt_batches")
        .select("*")
        .order("start_date", desc=True)
        .execute()
    )

    return response.data or []


def update_yogurt_status(
    batch_id,
    status,
):
    supabase = get_supabase_client()

    return (
        supabase
        .table("yogurt_batches")
        .update({
            "status": status,
        })
        .eq("id", batch_id)
        .execute()
    )


def delete_yogurt_batch(batch_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("yogurt_batches")
        .delete()
        .eq("id", batch_id)
        .execute()
    )