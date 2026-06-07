import sys
from pathlib import Path

import streamlit as st
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from utils.supabase_client import get_supabase_client

def update_plan_active_status(plan_id, is_active):
    supabase = get_supabase_client()

    return (
        supabase
        .table("pingping_supplement_plans")
        .update({"is_active": is_active})
        .eq("id", plan_id)
        .execute()
    )

def render_pingping_plan():
    st.subheader("Pingping Supplement Plan")

    supabase = get_supabase_client()

    with st.form("add_pingping_plan_form", clear_on_submit=True):
        supplement_name = st.text_input("Supplement Name")
        dosage = st.text_input("Dosage", placeholder="e.g. 500mg, 1 capsule, etc.")
        frequency = st.text_input("Frequency", placeholder="e.g. Once daily, Twice daily, etc.")
        timing = st.text_input("Timing", placeholder="e.g. after breakfast, before bed, etc.")

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date")
        with col2:
            end_date = st.date_input("End Date")

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Supplement Plan")

        if submitted:
            data = {
                "supplement_name": supplement_name.strip(),
                "dosage": dosage.strip(),
                "frequency": frequency.strip(),
                "timing": timing.strip(),
                "start_date": str(start_date),
                "end_date": str(end_date),
                "notes": notes.strip(),
                "is_active": True,
            }

            supabase.table("pingping_supplement_plans").insert(data).execute()
            st.success("Supplement plan added successfully 💊")

    st.divider()

    st.subheader("Current Supplement Plans")

    result = (
        supabase
        .table("pingping_supplement_plans")
        .select("*")
        .order("start_date", desc=True)
        .execute()
    )

    records = result.data

    if not records:
        st.info("No supplement plans found.")
        return
    
    df = pd.DataFrame(records)
    df["start_date"] = pd.to_datetime(df["start_date"])
    df["end_date"] = pd.to_datetime(df["end_date"])

    show_active_only = st.checkbox("Show Active Plans Only", value=True)

    if show_active_only:
        df = df[df["is_active"] == True]

    if df.empty:
        st.info("No active supplement plans found.")
        return

    display_columns = [
        "supplement_name",
        "dosage",
        "frequency",
        "timing",
        "start_date",
        "end_date",
        "notes",
        "is_active",
    ]

    st.dataframe(
        df[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Update Plan Status")

    plan_options = {
        f'{row["supplement_name"]} | {row["dosage"]} | {row["timing"]} | active={row["is_active"]}': row["id"]
        for _, row in df.iterrows()
    }

    if plan_options:
        selected_plan = st.selectbox(
            "Choose plan",
            list(plan_options.keys())
        )

        new_status = st.selectbox(
            "New Status",
            [True, False],
            format_func=lambda x: "Active" if x else "Inactive"
        )

        if st.button("Update Plan Status", use_container_width=True):
            update_plan_active_status(plan_options[selected_plan], new_status)
            st.success("Plan status updated.")
            st.rerun()