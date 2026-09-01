from utils.supplement_db import (
    get_all_supplements as db_get_all_supplements,
    add_supplement as db_add_supplement,
    update_supplement as db_update_supplement,
    delete_supplement as db_delete_supplement,
    get_all_bottles as db_get_all_bottles,
    get_active_bottles_by_supplement as db_get_active_bottles_by_supplement,
    add_bottle as db_add_bottle,
    update_bottle as db_update_bottle,
    delete_bottle as db_delete_bottle,
)

from services.supplement_service import (
    enrich_bottle_with_remaining,
    build_bottle_label,
)


# ---------- Supplement Library ----------

def get_all_supplements():
    return db_get_all_supplements()


def get_active_bottles_by_supplement(supplement_id):
    bottles = db_get_active_bottles_by_supplement(
        supplement_id
    )

    available_bottles = []

    for bottle in bottles:
        enriched_bottle = enrich_bottle_with_remaining(
            bottle
        )
        if enriched_bottle["remaining"] > 0:
            available_bottles.append(
                enriched_bottle
            )

    return available_bottles


def get_active_supplements():
    return [
        item
        for item in get_all_supplements()
        if item["is_active"]
    ]


def add_supplement(
    name,
    category,
    default_unit,
    description,
    notes,
):
    return db_add_supplement(
        name,
        category,
        default_unit,
        description,
        notes,
    )


def update_supplement_status(
    supplement_id,
    is_active,
):
    return db_update_supplement(
        supplement_id,
        is_active,
    )


def delete_supplement(supplement_id):
    return db_delete_supplement(
        supplement_id
    )


# ---------- Bottles ----------

def get_all_bottles():
    return db_get_all_bottles()


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
    return db_add_bottle(
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
    )


def update_bottle(
    bottle_id,
    update_data,
):
    return db_update_bottle(
        bottle_id,
        update_data,
    )


def delete_bottle(bottle_id):
    return db_delete_bottle(
        bottle_id
    )


def get_bottle_rows():
    bottles = db_get_all_bottles()

    rows = []

    for bottle in bottles:
        enriched_bottle = enrich_bottle_with_remaining(
            bottle
        )

        supplement = (
            enriched_bottle.get("supplements")
            or {}
        )

        rows.append({
            "id": enriched_bottle["id"],
            "supplement": supplement.get("name"),
            "brand": enriched_bottle.get("brand"),
            "product_name": enriched_bottle.get("product_name"),
            "strength": enriched_bottle.get("strength"),
            "initial_quantity": (
                enriched_bottle.get("initial_quantity")
                or enriched_bottle.get("quantity")
            ),
            "remaining": enriched_bottle["remaining"],
            "unit": enriched_bottle.get("unit"),
            "purchase_date": enriched_bottle.get("purchase_date"),
            "expiry_date": enriched_bottle.get("expiry_date"),
            "opened_date": enriched_bottle.get("opened_date"),
            "finished_date": enriched_bottle.get("finished_date"),
            "status": enriched_bottle.get("status"),
            "notes": enriched_bottle.get("notes"),
        })

    return rows


def get_available_bottle_options():
    supplements = get_active_supplements()

    bottle_options = {}

    for supplement in supplements:
        bottles = get_active_bottles_by_supplement(
            supplement["id"]
        )

        for bottle in bottles:
            label = build_bottle_label(
                supplement,
                bottle,
            )

            bottle_options[label] = {
                "supplement": supplement,
                "bottle": bottle,
                "remaining": bottle["remaining"],
            }

    return bottle_options