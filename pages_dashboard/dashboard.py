import streamlit as st
import pandas as pd
from datetime import date

from utils.supabase_client import get_supabase_client
from utils.home_db import get_meals_by_date, get_expiring_inventory_items, get_shopping_items, get_all_chores
from utils.time_utils import today_bj_date

from services.dashboard_service import (
    get_personal_dashboard,
    get_home_dashboard,
    get_lifestyle_dashboard,
    get_period_dashboard,
)

def render_attention(attention_items):
    st.markdown("### Attention")

    if attention_items:
        for item in attention_items:
            st.warning(item)
    else:
        st.success("Nothing urgent today.")


def render_personal(
    vera_logs,
    completed_pingping,
    total_pingping,
):
    st.markdown("### 👤 Personal")

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.metric(
                "Vera",
                f"{vera_logs} log(s)"
            )
    with col2:
        with st.container(border=True):
            st.metric(
                "Ping Ping",
                f"{completed_pingping}/{total_pingping}"
            )

def render_chores(
    todo_chores,
    completed_chores,
):
    st.divider()

    st.markdown("### 🧹 Chores")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.metric(
                "To Do",
                len(todo_chores),
            )

    with col2:
        with st.container(border=True):
            st.metric(
                "Completed",
                len(completed_chores),
            )

    if not todo_chores:
        return

    st.markdown("#### Pending Chores")

    for chore in todo_chores:

        with st.container(border=True):

            st.markdown(
                f"☐ **{chore['title']}**"
            )

            st.caption(
                f"Created {chore['created_at']}"
            )


def render_shopping(
    shopping_pending,
    shopping_purchased,
):
    st.divider()

    st.markdown("### 🛒 Shopping")

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.metric(
                "To Buy",
                len(shopping_pending),
            )

    with col2:
        with st.container(border=True):
            st.metric(
                "Purchased",
                len(shopping_purchased),
            )

    if not shopping_pending:
        return

    st.markdown("#### Shopping List")

    for item in shopping_pending:

        with st.container(border=True):

            st.markdown(
                f"**{item['name']}**"
            )

            details = []

            if item.get("category"):
                details.append(item["category"])

            if item.get("quantity"):

                qty = f"{item['quantity']:g}"

                if item.get("unit"):
                    qty += f" {item['unit']}"

                details.append(qty)

            if details:
                st.caption(
                    " · ".join(details)
                )

            notes = (
                item.get("notes") or ""
            ).strip()

            if notes:
                st.caption(
                    f"📝 {notes}"
                )


def render_fermentation(
    active_kombucha,
    oldest_kombucha_days,
    oldest_kombucha_name,
):
    st.divider()

    st.markdown("### 🌱 Fermentation")

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Active Kombucha",
            len(active_kombucha),
        )

    with col2:

        if oldest_kombucha_days is None:

            st.metric(
                "Oldest Batch",
                "-",
            )

        else:

            st.metric(
                "Oldest Batch",
                f"Day {oldest_kombucha_days}",
            )

    if oldest_kombucha_name:

        st.caption(
            f"{oldest_kombucha_name} · Day {oldest_kombucha_days}"
        )


def render_ballet(
    ballet_hours,
    ballet_this_month_hours,
    last_class,
):
    st.divider()

    st.markdown("### 🩰 Ballet")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Total",
            f"{ballet_hours:.1f} hrs",
        )

    with col2:

        st.metric(
            "This Month",
            f"{ballet_this_month_hours:.1f} hrs",
        )

    if last_class:

        st.caption(
            f'{last_class["class_date"]} · '
            f'{last_class.get("studio") or ""} · '
            f'{last_class.get("teacher") or ""}'
        )



def render_low_stock(low_stock_supplements):

    if not low_stock_supplements:
        return

    st.divider()

    st.subheader("Low Stock Supplements")

    for item in low_stock_supplements:

        st.warning(
            f'{item["supplement_name"]} | '
            f'{item["brand"]} | '
            f'{item["remaining"]:g} {item["unit"]} left'
        )

def render_meals(meals_today):

    st.markdown("#### 🍽️ Meals Today")

    if not meals_today:
        st.caption("No meals logged today.")
        return

    for meal in meals_today:

        with st.container(border=True):

            st.markdown(
                f"**{meal['meal_type']}**"
            )

            st.write(
                meal["content"]
            )

            if meal.get("created_at"):
                st.caption(
                    meal["created_at"]
                )

def render_inventory(expiring_items):

    st.markdown("#### 🧊 Expiring Inventory")

    if expiring_items:
        st.caption(
            f"{len(expiring_items)} item(s) need attention"
        )

    if not expiring_items:
        st.caption("No items expiring within 3 days.")
        return

    for item in expiring_items:

        days = item["days_until_expiry"]

        if days < 0:
            icon = "❌"
            message = f"Expired {-days} day(s) ago"

        elif days == 0:
            icon = "🔴"
            message = "Expires today"

        elif days == 1:
            icon = "🟠"
            message = "Expires tomorrow"

        else:
            icon = "🟢"
            message = f"Expires in {days} days"

        with st.container(border=True):

            st.markdown(
                f"**{item['name']}**"
            )

            details = []

            if item.get("category"):
                details.append(item["category"])

            qty = f"{item['quantity']:g}"

            if item.get("unit"):
                qty += f" {item['unit']}"

            details.append(qty)

            if item.get("location"):
                details.append(
                    f"📍 {item['location']}"
                )

            st.caption(
                " · ".join(details)
            )

            st.markdown(
                f"{icon} {message}"
            )

            notes = (
                item.get("notes") or ""
            ).strip()

            if notes:
                st.caption(
                    f"📝 {notes}"
                )




def render_dashboard():
    st.subheader("Today Overview")

    supabase = get_supabase_client()
    today_date = today_bj_date()
    today = str(today_date)

    # ---------------- Data ----------------

    # Personal Dashboard
    personal = get_personal_dashboard(today)
    vera_supplement_logs = personal["vera_logs"]
    completed_pingping = personal["completed_pingping"]
    total_pingping = personal["total_pingping"]
    low_stock_supplements = personal["low_stock"]

    # Home Dashboard
    home = get_home_dashboard(today)
    meals_today = home["meals_today"]
    expiring_items = home["expiring_items"]
    shopping_pending = home["shopping_pending"]
    shopping_purchased = home["shopping_purchased"]
    todo_chores = home["todo_chores"]
    completed_chores = home["completed_chores"]

    # Lifestyle Dashboard
    lifestyle = get_lifestyle_dashboard(
        today,
        today_date,
    )

    active_kombucha = lifestyle["active_kombucha"]
    oldest_kombucha_days = lifestyle["oldest_kombucha_days"]
    oldest_kombucha_name = lifestyle["oldest_kombucha_name"]
    ballet_hours = lifestyle["ballet_hours"]
    ballet_this_month_hours = lifestyle["ballet_this_month_hours"]
    last_class = lifestyle["last_class"]

    # Period Dashboard
    period = get_period_dashboard(
        today,
        today_date,
    )

    cycle_day = period["cycle_day"]
    latest_period_start = period["latest_period_start"]
    latest_period_end = period["latest_period_end"]
    predicted_next_period = period["predicted_next_period"]
    days_until_next_period = period["days_until_next_period"]
    today_daily_log = period["today_daily_log"]



    # Attention Center
    attention_items = []

    if low_stock_supplements:
        attention_items.append(
            f"{len(low_stock_supplements)} supplement bottle(s) low in stock."
        )

    if cycle_day is not None:
        if cycle_day <= 3:
            attention_items.append(
                f"Cycle Day {cycle_day}. Take it easy if needed."
            )
        elif 12 <= cycle_day <= 18:
            attention_items.append(
                f"Cycle Day {cycle_day}. Possible fertile window."
            )
        elif cycle_day >= 28:
            attention_items.append(
                f"Cycle Day {cycle_day}. Period may be approaching."
            )

    remaining_pingping = total_pingping - completed_pingping

    if remaining_pingping > 0:
        attention_items.append(
            f"Pingping has {remaining_pingping} supplement(s) unchecked today."
        )

    if todo_chores:
        attention_items.append(
            f"{len(todo_chores)} chore(s) still pending."
        )

    expiring_today = [
        item for item in expiring_items
        if item["days_until_expiry"] == 0
    ]

    expired_items = [
        item for item in expiring_items
        if item["days_until_expiry"] < 0
    ]

    if oldest_kombucha_days is not None:
        if oldest_kombucha_days >= 14:
            attention_items.append(
                f"Kombucha is on Day {oldest_kombucha_days}. It may be getting quite sour."
            )
        elif oldest_kombucha_days >= 7:
            attention_items.append(
                f"Kombucha is on Day {oldest_kombucha_days}. Good time to taste-check."
            )



    # ---------------- Display ----------------

    render_attention(attention_items)

    render_personal(
        len(vera_supplement_logs),
            completed_pingping,
            total_pingping
    )

    render_low_stock(
        low_stock_supplements,
    )

    render_meals(
        meals_today,
    )

    render_inventory(
        expiring_items,
    )

    render_chores(
        todo_chores,
        completed_chores
    )

    render_shopping(
        shopping_pending,
        shopping_purchased
    )

    render_fermentation(
        active_kombucha,
        oldest_kombucha_days,
        oldest_kombucha_name
    )

    render_ballet(
        ballet_hours,
        ballet_this_month_hours,
        last_class
    )
    