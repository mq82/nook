from utils.supplement_db import (
    add_supplement_intake as db_add_supplement_intake,
    add_legacy_supplement_log as db_add_legacy_supplement_log,
    delete_supplement_intake as db_delete_supplement_intake,
    delete_supplement_log as db_delete_supplement_log,
    get_supplement_intakes_by_date as db_get_supplement_intakes_by_date,
    get_supplement_logs_by_date as db_get_supplement_logs_by_date,
)

# ---------- Tracking CRUD ----------

def add_supplement_intake(
    person_name,
    supplement_id,
    bottle_id,
    amount,
    unit,
    notes,
):
    return db_add_supplement_intake(
        person_name,
        supplement_id,
        bottle_id,
        amount,
        unit,
        notes,
    )


def add_legacy_supplement_log(
    supplement_name,
    dosage,
    unit,
    note,
):
    return db_add_legacy_supplement_log(
        supplement_name,
        dosage,
        unit,
        note,
    )


def delete_supplement_intake(intake_id):
    return db_delete_supplement_intake(
        intake_id
    )


def delete_supplement_log(log_id):
    return db_delete_supplement_log(
        log_id
    )


def get_supplement_intakes_by_date(date):
    return db_get_supplement_intakes_by_date(
        date
    )


def get_supplement_logs_by_date(date):
    return db_get_supplement_logs_by_date(
        date
    )


# ---------- Business Logic ----------

# ---------- Daily Summary -----------

def get_supplement_intake_daily_summary(date):

    intakes = db_get_supplement_intakes_by_date(date)
    summary_map = {}

    for intake in intakes:

        key = (
            intake["supplement_name"],
            intake["unit"],
        )

        summary_map[key] = (
            summary_map.get(key, 0)
            + float(intake["amount"] or 0)
        )

    summary = []

    for (
        supplement_name,
        unit,
    ), total_amount in summary_map.items():

        summary.append({
            "supplement_name": supplement_name,
            "total_amount": total_amount,
            "unit": unit,
        })

    summary.sort(
        key=lambda x: x["supplement_name"]
    )

    return summary


def get_supplement_daily_summary(date):

    logs = db_get_supplement_logs_by_date(date)
    summary_map = {}

    for log in logs:

        key = (
            log["supplement_name"],
            log["unit"],
        )

        summary_map[key] = (
            summary_map.get(key, 0)
            + float(log["dosage"] or 0)
        )

    summary = []

    for (
        supplement_name,
        unit,
    ), total_dosage in summary_map.items():

        summary.append({
            "supplement_name": supplement_name,
            "total_dosage": total_dosage,
            "unit": unit,
        })

    summary.sort(
        key=lambda x: x["supplement_name"]
    )

    return summary