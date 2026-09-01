import streamlit as st
import pandas as pd

from utils.home_db import (
    add_chore as db_add_chore,
    get_all_chores as db_get_all_chores,
    complete_chore as db_complete_chore,
    undo_chore as db_undo_chore,
    delete_chore as db_delete_chore,
    add_meal as db_add_meal,
    get_meals_by_date as db_get_meals_by_date,
    delete_meal as db_delete_meal,
    add_inventory_item as db_add_inventory_item,
    get_inventory_items as db_get_inventory_items,
    delete_inventory_item as db_delete_inventory_item,
    add_shopping_item as db_add_shopping_item,
    get_shopping_items as db_get_shopping_items,
    mark_shopping_item_purchased as db_mark_shopping_item_purchased,
    undo_shopping_item as db_undo_shopping_item,
    delete_shopping_item as db_delete_shopping_item,
)
from utils.time_utils import format_bj_time, today_bj_date


# ---------- Chores ----------

def add_chore(title):
    return db_add_chore(title)


def get_all_chores():
    chores = db_get_all_chores()

    todo = []
    completed = []

    for chore in chores:
        if chore["completed"]:
            completed.append(chore)
        else:
            todo.append(chore)

    todo.sort(
        key=lambda item: item["created_at"]
    )

    completed.sort(
        key=lambda item: item["completed_at"],
        reverse=True,
    )

    return {
        "todo": todo,
        "completed": completed,
    }


def complete_chore(chore_id, user_name):
    return db_complete_chore(chore_id, user_name)


def undo_chore(chore_id):
    return db_undo_chore(chore_id)


def delete_chore(chore_id):
    return db_delete_chore(chore_id)


# ---------- Meals ----------

def add_meal(meal_date, meal_type, content):
    return db_add_meal(
        meal_date,
        meal_type,
        content,
    )


def get_meals_by_date(meal_date):
    meals = db_get_meals_by_date(meal_date)
    meal_order = {
        "Breakfast": 1,
        "Lunch": 2,
        "Dinner": 3,
        "Snack": 4,
        "Other": 5,
    }

    formatted = []

    for meal in meals:
        formatted.append({
            "id": meal["id"],
            "meal_date": meal["meal_date"],
            "meal_type": meal["meal_type"],
            "content": meal["content"],
            "created_at": format_bj_time(
                meal["created_at"]
            ),
        })

    formatted.sort(
        key=lambda meal: (
            meal_order.get(
                meal["meal_type"],
                99,
            ),
            meal["created_at"],
        )
    )

    return formatted


def delete_meal(meal_id):
    return db_delete_meal(meal_id)


# ---------- Inventory ----------

def add_inventory_item(
    name,
    category,
    location,
    quantity,
    unit,
    purchase_date,
    expiry_date,
    notes,
):
    return db_add_inventory_item(
        name,
        category,
        location,
        quantity,
        unit,
        purchase_date,
        expiry_date,
        notes,
    )


def get_inventory_items():
    items = db_get_inventory_items()
    today = today_bj_date()

    for item in items:
        expiry_date = item.get("expiry_date")
        if expiry_date:
            expiry_date = pd.to_datetime(
                expiry_date
            ).date()

            item["days_until_expiry"] = (
                expiry_date - today
            ).days
        else:
            item["days_until_expiry"] = None

    items.sort(
        key=lambda item: (
            item.get("expiry_date") or "9999-12-31",
            item["name"].lower(),
        )
    )

    return items


def get_expiring_inventory_items(days=3):
    items = get_inventory_items()

    expiring_items = [
        item
        for item in items
        if (
            item["days_until_expiry"] is not None
            and item["days_until_expiry"] <= days
        )
    ]

    expiring_items.sort(
        key=lambda item: (
            item["days_until_expiry"],
            item["name"].lower(),
        ),
    )

    for item in expiring_items:
        days_left = item["days_until_expiry"]

        if days_left < 0:
            item["status_icon"] = "❌"
            item["status_text"] = (
                f"Expired {-days_left} day(s) ago"
            )

        elif days_left == 0:
            item["status_icon"] = "🔴"
            item["status_text"] = "Expires today"

        elif days_left == 1:
            item["status_icon"] = "🟠"
            item["status_text"] = "Expires tomorrow"

        else:
            item["status_icon"] = "🟢"
            item["status_text"] = (
                f"Expires in {days_left} day(s)"
            )

    return expiring_items


def delete_inventory_item(item_id):
    return db_delete_inventory_item(item_id)


# ---------- Shopping ----------

def add_shopping_item(
    name,
    category,
    quantity,
    unit,
    notes,
):
    return db_add_shopping_item(
        name,
        category,
        quantity,
        unit,
        notes,
    )


def get_shopping_items():
    items = db_get_shopping_items()

    pending = []
    purchased = []

    for item in items:
        if item["is_purchased"]:
            purchased.append(item)
        else:
            pending.append(item)

    pending.sort(
        key=lambda item: item["name"].lower()
    )

    purchased.sort(
        key=lambda item: item.get("purchased_at") or "",
        reverse=True,
    )

    return {
        "pending": pending,
        "purchased": purchased,
    }


def mark_shopping_item_purchased(item_id):
    return db_mark_shopping_item_purchased(item_id)


def undo_shopping_item(item_id):
    return db_undo_shopping_item(item_id)


def delete_shopping_item(item_id):
    return db_delete_shopping_item(item_id)