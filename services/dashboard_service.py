from services.home_service import (
    get_meals_by_date,
    get_expiring_inventory_items,
    get_shopping_items,
    get_all_chores,
)
from services.supplement_tracking_service import (
    get_supplement_intakes_by_date,
)
from services.supplement_library_service import (
    get_bottle_rows,
)
from services.pingping_checkin_service import (
    get_checkin_data,
    get_checkin_progress,
)
from services.fermentation_service import (
    get_kombucha_rows,
    get_kombucha_summary,
)
from services.ballet_service import (
    get_ballet_dashboard_summary,
)
from services.period_service import (
    get_period_dashboard_summary,
)

def get_low_stock_supplement_bottles(threshold=10):
    bottles = get_bottle_rows()

    low_stock = []

    for bottle in bottles:
        if (
            bottle["status"] == "active"
            and bottle["remaining"] <= threshold
        ):
            low_stock.append({
                "supplement_name": bottle["supplement"] or "",
                "brand": bottle["brand"] or "",
                "product_name": bottle["product_name"] or "",
                "remaining": bottle["remaining"],
                "unit": bottle["unit"] or "",
            })

    return low_stock


def get_personal_dashboard(today):
    """
    Dashboard data for the Personal section.
    """

    # ---------- Pingping ----------

    checkin_data = get_checkin_data(today)

    checkin_progress = get_checkin_progress(
        checkin_data["plans"],
        checkin_data["checkins"],
    )

    completed_pingping = checkin_progress[
        "completed"
    ]

    total_pingping = checkin_progress[
        "total"
    ]

    # ---------- Vera ----------

    vera_logs = get_supplement_intakes_by_date(
        today
    )

    return {
        "vera_logs": vera_logs,
        "completed_pingping": completed_pingping,
        "total_pingping": total_pingping,
        "low_stock": get_low_stock_supplement_bottles(),
    }



def get_home_dashboard(today):
    """
    Dashboard data for the Home section.
    """

    meals_today = get_meals_by_date(today)

    expiring_items = get_expiring_inventory_items(days=3)

    shopping = get_shopping_items()
    chores = get_all_chores()

    return {
        "meals_today": meals_today,
        "expiring_items": expiring_items,
        "shopping_pending": shopping["pending"],
        "shopping_purchased": shopping["purchased"],
        "todo_chores": chores["todo"],
        "completed_chores": chores["completed"],
    }



def get_lifestyle_dashboard(today, today_date):
    """
    Dashboard data for Lifestyle section.
    """

    # ---------- Kombucha ----------

    kombucha_rows = get_kombucha_rows()

    kombucha_summary = get_kombucha_summary(
        kombucha_rows
    )

    active_kombucha = [
        row
        for row in kombucha_rows
        if row["status"] == "Active"
    ]

    oldest_batch = kombucha_summary[
        "oldest_batch"
    ]

    if oldest_batch:
        oldest_kombucha_days = oldest_batch[
            "fermentation_days"
        ]

        oldest_kombucha_name = oldest_batch[
            "batch_name"
        ]
    else:
        oldest_kombucha_days = None
        oldest_kombucha_name = None

    # ---------- Ballet ----------

    ballet_summary = (
        get_ballet_dashboard_summary(
            today_date
        )
    )

    return {
        "active_kombucha": active_kombucha,
        "oldest_kombucha_days": oldest_kombucha_days,
        "oldest_kombucha_name": oldest_kombucha_name,
        "ballet_hours": ballet_summary["total_hours"],
        "ballet_this_month_hours": ballet_summary["this_month_hours"],
        "last_class": ballet_summary["last_class"],
    }


def get_period_dashboard(today, today_date):
    return get_period_dashboard_summary(
        today_date
    )