import pandas as pd

from utils.fermentation_db import (
    add_kombucha_batch as db_add_kombucha_batch,
    get_all_kombucha_batches as db_get_all_kombucha_batches,
    update_kombucha_status as db_update_kombucha_status,
    add_pickle_batch as db_add_pickle_batch,
    get_all_pickle_batches as db_get_all_pickle_batches,
    update_pickle_status as db_update_pickle_status,
    delete_pickle_batch as db_delete_pickle_batch,
    add_yogurt_batch as db_add_yogurt_batch,
    get_all_yogurt_batches as db_get_all_yogurt_batches,
    update_yogurt_status as db_update_yogurt_status,
    delete_yogurt_batch as db_delete_yogurt_batch,
)


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
    return db_add_kombucha_batch(
        batch_name=batch_name,
        start_date=start_date,
        tea_type=tea_type,
        sugar_grams=sugar_grams,
        liquid_ml=liquid_ml,
        starter_description=starter_description,
        status=status,
        notes=notes,
    )


def update_kombucha_status(
    batch_id,
    status,
):
    return db_update_kombucha_status(
        batch_id,
        status,
    )


def get_kombucha_rows():
    batches = db_get_all_kombucha_batches()

    if not batches:
        return []

    today = pd.Timestamp.today().normalize()

    rows = []

    for batch in batches:
        start_date = pd.to_datetime(
            batch["start_date"]
        )

        fermentation_days = (
            today - start_date.normalize()
        ).days

        rows.append({
            "id": batch["id"],
            "batch_name": batch.get("batch_name"),
            "start_date": batch.get("start_date"),
            "fermentation_days": fermentation_days,
            "tea_type": batch.get("tea_type"),
            "sugar_grams": batch.get("sugar_grams"),
            "liquid_ml": batch.get("liquid_ml"),
            "starter_description": batch.get("starter_description"),
            "status": batch.get("status"),
            "notes": batch.get("notes"),
        })

    return rows


def get_kombucha_summary(rows):
    active_rows = [
        row
        for row in rows
        if row["status"] == "Active"
    ]

    if not active_rows:
        return {
            "active_count": 0,
            "oldest_batch": None,
        }

    oldest_batch = max(
        active_rows,
        key=lambda row: row["fermentation_days"],
    )

    return {
        "active_count": len(active_rows),
        "oldest_batch": oldest_batch,
    }

# ---------- Pickles ----------

def calculate_pickle_salt_percentage(
    salt_g,
    water_ml,
    ingredient_weight_g,
    method,
):
    if method == "Brine":
        if water_ml <= 0:
            return None, None

        percentage = round(
            salt_g / water_ml * 100,
            2,
        )

        return percentage, "Water"

    if method == "Dry Salt":
        if ingredient_weight_g <= 0:
            return None, None

        percentage = round(
            salt_g / ingredient_weight_g * 100,
            2,
        )

        return percentage, "Ingredient"

    return None, None


def add_pickle_batch(
    batch_name,
    start_date,
    ingredient,
    ingredient_weight_g,
    salt_g,
    water_ml,
    method,
    notes,
):
    salt_percentage, salt_percentage_basis = (
        calculate_pickle_salt_percentage(
            salt_g=salt_g,
            water_ml=water_ml,
            ingredient_weight_g=ingredient_weight_g,
            method=method,
        )
    )

    return db_add_pickle_batch(
        batch_name=batch_name,
        start_date=start_date,
        ingredient=ingredient,
        ingredient_weight_g=ingredient_weight_g,
        salt_g=salt_g,
        water_ml=water_ml,
        salt_percentage=salt_percentage,
        salt_percentage_basis=salt_percentage_basis,
        method=method,
        notes=notes,
    )


def update_pickle_status(
    batch_id,
    status,
):
    return db_update_pickle_status(
        batch_id,
        status,
    )


def delete_pickle_batch(batch_id):
    return db_delete_pickle_batch(
        batch_id
    )


def get_pickle_rows():
    batches = db_get_all_pickle_batches()
    if not batches:
        return []

    today = pd.Timestamp.today().normalize()
    rows = []

    for batch in batches:
        start_date = pd.to_datetime(
            batch["start_date"]
        )

        fermentation_days = (
            today - start_date.normalize()
        ).days

        rows.append({
            "id": batch["id"],
            "batch_name": batch.get("batch_name"),
            "start_date": batch.get("start_date"),
            "fermentation_days": fermentation_days,
            "ingredient": batch.get("ingredient"),
            "ingredient_weight_g": batch.get(
                "ingredient_weight_g"
            ),
            "salt_g": batch.get("salt_g"),
            "water_ml": batch.get("water_ml"),
            "salt_percentage": batch.get(
                "salt_percentage"
            ),
            "salt_percentage_basis": batch.get(
                "salt_percentage_basis"
            ),
            "method": batch.get("method"),
            "status": batch.get("status"),
            "notes": batch.get("notes"),
        })

    return rows


def get_pickle_summary(rows):
    active_rows = [
        row
        for row in rows
        if row["status"] == "Active"
    ]

    if not active_rows:
        return {
            "active_count": 0,
            "oldest_batch": None,
        }

    oldest_batch = max(
        active_rows,
        key=lambda row: row["fermentation_days"],
    )

    return {
        "active_count": len(active_rows),
        "oldest_batch": oldest_batch,
    }

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
    return db_add_yogurt_batch(
        batch_name=batch_name,
        start_date=start_date,
        start_time=start_time,
        milk_type=milk_type,
        milk_volume_ml=milk_volume_ml,
        starter_type=starter_type,
        starter_amount=starter_amount,
        incubation_temperature_c=incubation_temperature_c,
        incubation_hours=incubation_hours,
        strained=strained,
        yield_ml=yield_ml,
        notes=notes,
    )


def update_yogurt_status(
    batch_id,
    status,
):
    return db_update_yogurt_status(
        batch_id,
        status,
    )


def delete_yogurt_batch(batch_id):
    return db_delete_yogurt_batch(
        batch_id
    )


def get_yogurt_rows():
    batches = db_get_all_yogurt_batches()
    if not batches:
        return []

    rows = []

    for batch in batches:
        rows.append({
            "id": batch["id"],
            "batch_name": batch.get("batch_name"),
            "start_date": batch.get("start_date"),
            "start_time": batch.get("start_time"),
            "milk_type": batch.get("milk_type"),
            "milk_volume_ml": batch.get(
                "milk_volume_ml"
            ),
            "starter_type": batch.get(
                "starter_type"
            ),
            "starter_amount": batch.get(
                "starter_amount"
            ),
            "incubation_temperature_c": batch.get(
                "incubation_temperature_c"
            ),
            "incubation_hours": batch.get(
                "incubation_hours"
            ),
            "strained": batch.get("strained"),
            "yield_ml": batch.get("yield_ml"),
            "status": batch.get("status"),
            "notes": batch.get("notes"),
        })

    return rows


def get_yogurt_summary(rows):
    active_rows = [
        row
        for row in rows
        if row["status"] == "Active"
    ]

    finished_rows = [
        row
        for row in rows
        if row["status"] == "Finished"
    ]

    return {
        "active_count": len(active_rows),
        "finished_count": len(finished_rows),
    }