import streamlit as st
import pandas as pd
from datetime import date

from services.pingping_checkin_service import (
    get_checkin_data,
    save_plan_checkin,
    get_checkin_progress,
    get_checkin_rows,
)


def render_pingping_checkin():
    st.subheader("Pingping Daily Check")

    checkin_date = st.date_input(
        "Check-in Date",
        value=date.today(),
    )

    data = get_checkin_data(
        checkin_date
    )

    plans = data["plans"]
    checkins = data["checkins"]

    if not plans:
        st.info(
            "No active supplement plans for this date."
        )
        return

    st.write(
        f"Plans for {checkin_date}"
    )

    for plan in plans:
        plan_id = plan["id"]

        existing = checkins.get(
            plan_id
        )

        already_taken = (
            existing["is_taken"]
            if existing
            else False
        )

        label = (
            f'{plan["timing"] or "No timing"} - '
            f'{plan["supplement_name"]} - '
            f'{plan["dosage"] or ""} - '
            f'{plan["frequency"] or ""}'
        )

        taken = st.checkbox(
            label,
            value=already_taken,
            key=(
                f"pingping_checkin_"
                f"{plan_id}_"
                f"{checkin_date}"
            ),
        )

        if taken != already_taken:
            save_plan_checkin(
                plan_id=plan_id,
                checkin_date=checkin_date,
                is_taken=taken,
            )

            st.rerun()

    st.divider()

    progress_data = get_checkin_progress(
        plans,
        checkins,
    )

    st.metric(
        "Today Progress",
        (
            f'{progress_data["completed"]}/'
            f'{progress_data["total"]}'
        ),
    )

    st.progress(
        progress_data["progress"]
    )

    st.divider()
    st.subheader("Today Details")

    rows = get_checkin_rows(
        plans,
        checkins,
    )

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )