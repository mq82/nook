import streamlit as st
import pandas as pd
from datetime import date

from utils.supabase_client import get_supabase_client
from utils.home_db import get_meals_by_date, get_expiring_inventory_items
from utils.time_utils import today_bj_date


def render_dashboard():
    st.subheader("Today Overview")

    supabase = get_supabase_client()
    today_date = today_bj_date()
    today = str(today_date)

    # ---------------- Data ----------------

    # Pingping supplements
    plans_result = (
        supabase
        .table("pingping_supplement_plans")
        .select("*")
        .eq("is_active", True)
        .lte("start_date", today)
        .or_(f"end_date.is.null,end_date.gte.{today}")
        .execute()
    )

    active_plans = plans_result.data
    total_pingping = len(active_plans)
    active_plan_ids = {plan["id"] for plan in active_plans}

    checkins_result = (
        supabase
        .table("pingping_supplement_checkins")
        .select("*")
        .eq("checkin_date", today)
        .eq("is_taken", True)
        .execute()
    )

    completed_pingping = len([
        item for item in checkins_result.data
        if item["plan_id"] in active_plan_ids
    ])

    # Vera supplements
    supplement_result = (
        supabase
        .table("supplement_logs")
        .select("*")
        .gte("taken_at", f"{today}T00:00:00+08:00")
        .lt("taken_at", f"{today}T23:59:59+08:00")
        .execute()
    )

    vera_supplement_logs = supplement_result.data

    # Meals
    meals_today = get_meals_by_date(today)

    # Fridge
    expiring_items = get_expiring_inventory_items(days=3)

    # Kombucha
    kombucha_result = (
        supabase
        .table("kombucha_batches")
        .select("*")
        .eq("status", "Active")
        .order("start_date", desc=False)
        .execute()
    )

    active_kombucha = kombucha_result.data

    oldest_kombucha_days = None
    oldest_kombucha_name = None

    if active_kombucha:
        oldest = active_kombucha[0]
        start = pd.to_datetime(oldest["start_date"]).date()
        oldest_kombucha_days = (today_date - start).days
        oldest_kombucha_name = oldest["batch_name"]

    # Ballet
    ballet_result = (
        supabase
        .table("ballet_classes")
        .select("duration_hours")
        .execute()
    )

    ballet_hours = sum(
        item["duration_hours"] for item in ballet_result.data
    ) if ballet_result.data else 0

    # Ballet this month + last class
    current_month = today[:7]

    ballet_month_result = (
        supabase
        .table("ballet_classes")
        .select("*")
        .gte("class_date", f"{current_month}-01")
        .execute()
    )

    ballet_this_month_hours = sum(
        item["duration_hours"] for item in ballet_month_result.data
    ) if ballet_month_result.data else 0

    last_class_result = (
        supabase
        .table("ballet_classes")
        .select("*")
        .order("class_date", desc=True)
        .limit(1)
        .execute()
    )

    last_class = last_class_result.data[0] if last_class_result.data else None

    # Period tracker
    period_result = (
        supabase
        .table("cycle_periods")
        .select("*")
        .order("start_date", desc=True)
        .limit(1)
        .execute()
    )

    latest_period = period_result.data[0] if period_result.data else None

    cycle_day = None
    latest_period_start = None
    latest_period_end = None

    if latest_period:
        latest_period_start = pd.to_datetime(latest_period["start_date"]).date()
        latest_period_end = (
            pd.to_datetime(latest_period["end_date"]).date()
            if latest_period.get("end_date")
            else None
        )
        cycle_day = (today_date - latest_period_start).days + 1

    if latest_period_start:
        if latest_period_end:
            st.caption(
                f"Latest period: {latest_period_start} → {latest_period_end}"
            )
        else:
            st.caption(
                f"Latest period started on {latest_period_start}"
            )

    predicted_next_period = None
    days_until_next_period = None

    period_history_result = (
        supabase
        .table("cycle_periods")
        .select("*")
        .order("start_date", desc=False)
        .execute()
    )

    period_history = period_history_result.data

    if len(period_history) >= 2 and latest_period_start:
        period_df = pd.DataFrame(period_history)
        period_df["start_date"] = pd.to_datetime(period_df["start_date"])
        period_df = period_df.sort_values("start_date")

        period_df["cycle_length_days"] = (
            period_df["start_date"]
            .diff()
            .dt.days
        )

        recent_cycle_lengths = (
            period_df["cycle_length_days"]
            .dropna()
            .tail(6)
        )

        if not recent_cycle_lengths.empty:
            avg_cycle_length = int(round(recent_cycle_lengths.mean()))
            predicted_next_period = latest_period_start + pd.Timedelta(days=avg_cycle_length)
            days_until_next_period = (predicted_next_period - today_date).days

    if predicted_next_period is not None:
        st.caption(
            f"Estimated next period: {predicted_next_period} "
            f"({days_until_next_period} day(s) left)"
        )

    # Period daily log today
    daily_log_result = (
        supabase
        .table("daily_logs")
        .select("*")
        .eq("log_date", today)
        .limit(1)
        .execute()
    )

    today_daily_log = daily_log_result.data[0] if daily_log_result.data else None

    if today_daily_log:
        st.caption(
            f'Period daily log today: '
            f'energy {today_daily_log.get("energy_level")}/10 · '
            f'stress {today_daily_log.get("stress_level")}/10 · '
            f'pain {today_daily_log.get("lower_ab_pain")}/10'
        )
    else:
        st.caption("No period daily log today.")

    # Attention Center
    attention_items = []

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

    expiring_today = [
        item for item in expiring_items
        if item["days_until_expiry"] == 0
    ]

    expired_items = [
        item for item in expiring_items
        if item["days_until_expiry"] < 0
    ]

    if expired_items:
        attention_items.append(
            f"{len(expired_items)} fridge item(s) already expired."
        )

    if expiring_today:
        attention_items.append(
            f"{len(expiring_today)} fridge item(s) expire today."
        )

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
    st.markdown("### Attention")

    if attention_items:
        for item in attention_items:
            st.warning(item)
    else:
        st.success("Nothing urgent today.")

    st.divider()
    
    st.markdown("### Personal")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Vera Supplement Logs", len(vera_supplement_logs))

    with col2:
        st.metric("Pingping Supplements", f"{completed_pingping} / {total_pingping}")

    if vera_supplement_logs:
        st.caption("Vera supplements today")
        for item in vera_supplement_logs:
            st.markdown(
                f'- **{item["supplement_name"]}**: '
                f'{item["dosage"]} {item["unit"]}'
            )
        
    with col3:
        if cycle_day:
            st.metric("Cycle Day", f"Day {cycle_day}")
        else:
            st.metric("Cycle Day", "-")

    st.divider()

    st.markdown("### Home")

    col4, col5 = st.columns(2)

    with col4:
        st.metric("Meals Logged Today", len(meals_today))

    with col5:
        st.metric("Expiring Fridge Items", len(expiring_items))

    if meals_today:
        st.caption("Meals today")
        for meal in meals_today:
            st.markdown(
                f'- **{meal["meal_type"]}**: {meal["content"]}'
            )

    if expiring_items:
        st.caption("Expiring fridge items")
        for item in expiring_items:
            days_left = item["days_until_expiry"]

            if days_left < 0:
                status = f"Expired {-days_left} day(s) ago"
            elif days_left == 0:
                status = "Expires today"
            else:
                status = f"Expires in {days_left} day(s)"

            st.markdown(
                f'- **{item["name"]}** ({item["location"]}) — {status}'
            )

    st.divider()

    st.markdown("### Fermentation")

    col6, col7 = st.columns(2)

    with col6:
        st.metric("Active Kombucha Batches", len(active_kombucha))

    with col7:
        if oldest_kombucha_days is not None:
            st.metric("Oldest Kombucha Batch", f"Day {oldest_kombucha_days}")
        else:
            st.metric("Oldest Kombucha Batch", "-")

    if oldest_kombucha_name is not None:
        st.caption(
            f"Active kombucha: {oldest_kombucha_name} · Day {oldest_kombucha_days}"
        )

    st.divider()

    st.markdown("### Ballet")

    col8, col9 = st.columns(2)

    with col8:
        st.metric("Total Ballet Hours", f"{ballet_hours:.1f} hrs")

    with col9:
        st.metric("This Month", f"{ballet_this_month_hours:.1f} hrs")

    if last_class:
        st.caption(
            f'Last class: {last_class["class_date"]} · '
            f'{last_class.get("studio") or ""} · '
            f'{last_class.get("teacher") or ""}'
        )