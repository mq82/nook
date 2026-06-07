import streamlit as st
import pandas as pd
from datetime import date
from utils.supabase_client import get_supabase_client

def update_kombucha_status(batch_id, status):
    supabase = get_supabase_client()

    return (
        supabase
        .table("kombucha_batches")
        .update({"status": status})
        .eq("id", batch_id)
        .execute()
    )


def render_kombucha():

    st.subheader("Kombucha Tracker 🫙")

    supabase = get_supabase_client()

    with st.form("add_kombucha_batch_form", clear_on_submit=True):
        
        batch_name = st.text_input("Batch Name")

        start_date = st.date_input(
            "Start Date",
            value=date.today()
        )

        tea_type = st.text_input("Tea Type")

        sugar_grams = st.number_input(
            "Sugar (grams)",
            min_value=0.0,
            step=5.0
        )

        liquid_ml = st.number_input(
            "Liquid Volume (ml)",
            min_value=0.0,
            step=100.0
        )

        starter_description = st.text_input(
            "Starter Description",
            placeholder="e.g. wild grape culture / apple cider vinegar mother"
        )

        status = st.selectbox(
            "Status",
            [
                "Active",
                "Finished",
                "Discarded"
            ]
        )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Batch")

        if submitted:

            data = {
                "batch_name": batch_name,
                "start_date": str(start_date),
                "tea_type": tea_type,
                "sugar_grams": float(sugar_grams),
                "liquid_ml": float(liquid_ml),
                "starter_description": starter_description.strip(),
                "status": status,
                "notes": notes.strip()
            }

            supabase.table("kombucha_batches").insert(data).execute()

            st.success("Kombucha batch added successfully 🫙")

    st.divider()

    result = (
        supabase
        .table("kombucha_batches")
        .select("*")
        .order("start_date", desc=True)
        .execute()
    )

    records = result.data

    if not records:
        st.info("No kombucha batches yet.")
        return
    
    df = pd.DataFrame(records)

    df["start_date"] = pd.to_datetime(df["start_date"])

    today = pd.Timestamp.today()

    df["fermentation_days"] = (
        today - df["start_date"]
    ).dt.days

    st.subheader("Batches")

    display_columns = [
        "batch_name",
        "start_date",
        "fermentation_days",
        "tea_type",
        "sugar_grams",
        "liquid_ml",
        "starter_description",
        "status",
        "notes"
    ]

    st.dataframe(
        df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    active_df = df[df["status"] == "Active"]

    st.metric(
        "Active Batches",
        len(active_df)
    )

    if not active_df.empty:

        longest_batch = active_df.sort_values(
            "fermentation_days",
            ascending=False
        ).iloc[0]

        st.info(
            f'Oldest Active Batch: '
            f'{longest_batch["batch_name"]} '
            f'({longest_batch["fermentation_days"]} days)'
        )

    st.divider()
    st.subheader("Update Batch Status")

    batch_options = {
        f'{row["batch_name"]} | Day {row["fermentation_days"]} | {row["status"]}': row["id"]
        for _, row in df.iterrows()
    }

    if batch_options:
        selected_batch = st.selectbox(
            "Choose batch",
            list(batch_options.keys())
        )

        new_status = st.selectbox(
            "New Status",
            ["Active", "Finished", "Discarded"]
        )

        if st.button("Update Status", use_container_width=True):
            update_kombucha_status(batch_options[selected_batch], new_status)
            st.success("Batch status updated.")
            st.rerun()