from utils.supplement_db import (
    get_all_plans as db_get_all_plans,
    add_plan as db_add_plan,
    update_plan as db_update_plan,
    get_person_by_name as db_get_person_by_name,
)

from services.supplement_library_service import (
    get_active_supplements,
    get_active_bottles_by_supplement,
)

from services.supplement_service import (
    build_bottle_label,
)

def get_all_plans():
    return db_get_all_plans()


def add_plan(
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
    person = get_pingping()

    if not person:
        raise ValueError(
            "Pingping was not found in the people table."
        )

    return db_add_plan(
        person_id=person["id"],
        supplement_id=supplement_id,
        bottle_id=bottle_id,
        supplement_name=supplement_name,
        dosage=dosage,
        frequency=frequency,
        timing=timing,
        start_date=start_date,
        end_date=end_date,
        notes=notes,
    )


def update_plan_status(
    plan_id,
    is_active,
):
    return db_update_plan(
        plan_id,
        {
            "is_active": is_active,
        },
    )


def get_plan_rows():
    plans = get_all_plans()
    rows = []
    for plan in plans:
        supplement = plan.get("supplements") or {}
        bottle = plan.get("supplement_bottles") or {}
        person = plan.get("people") or {}

        bottle_label = " | ".join(
            part
            for part in [
                bottle.get("brand"),
                bottle.get("product_name"),
                bottle.get("strength"),
            ]
            if part
        )

        rows.append({
            "id": plan["id"],
            "person": person.get("name"),
            "supplement": supplement.get("name") or plan["supplement_name"],
            "bottle": bottle_label,
            "dosage": plan["dosage"],
            "frequency": plan["frequency"],
            "timing": plan["timing"],
            "start_date": plan["start_date"],
            "end_date": plan["end_date"],
            "notes": plan["notes"],
            "is_active": plan["is_active"],
        })

    return rows


def get_plan_form_data():
    supplements = get_active_supplements()
    supplement_map = {}

    for supplement in supplements:
        bottles = get_active_bottles_by_supplement(
            supplement["id"]
        )

        bottle_options = {}

        for bottle in bottles:
            label = build_bottle_label(
                supplement,
                bottle,
            )

            bottle_options[label] = bottle

        supplement_map[
            supplement["name"]
        ] = {
            "supplement": supplement,
            "bottles": bottle_options,
        }

    return {
        "supplement_names": list(
            supplement_map.keys()
        ),
        "supplement_options": supplement_map,
    }


def get_pingping():
    return db_get_person_by_name(
        "pingping"
    )