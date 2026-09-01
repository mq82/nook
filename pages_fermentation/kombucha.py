import streamlit as st
import pandas as pd
from datetime import date

from services.fermentation_service import (
    add_kombucha_batch,
    get_kombucha_rows,
    get_kombucha_summary,
    update_kombucha_status,
)


def render_kombucha():
    st.subheader("Kombucha Tracker 🫙")

    with st.form(
        "add_kombucha_batch_form",
        clear_on_submit=True,
    ):
        batch_name = st.text_input(
            "Batch Name"
        )

        start_date = st.date_input(
            "Start Date",
            value=date.today(),
        )

        tea_type = st.text_input(
            "Tea Type"
        )

        sugar_grams = st.number_input(
            "Sugar (grams)",
            min_value=0.0,
            step=5.0,
        )

        liquid_ml = st.number_input(
            "Liquid Volume (ml)",
            min_value=0.0,
            step=100.0,
        )

        starter_description = st.text_input(
            "Starter Description",
            placeholder=(
                "e.g. wild grape culture / "
                "apple cider vinegar mother"
            ),
        )

        status = st.selectbox(
            "Status",
            [
                "Active",
                "Finished",
                "Discarded",
            ],
        )

        notes = st.text_area(
            "Notes"
        )

        submitted = st.form_submit_button(
            "Add Batch"
        )

        if submitted:
            add_kombucha_batch(
                batch_name=batch_name.strip(),
                start_date=str(start_date),
                tea_type=tea_type.strip(),
                sugar_grams=float(sugar_grams),
                liquid_ml=float(liquid_ml),
                starter_description=starter_description.strip(),
                status=status,
                notes=notes.strip(),
            )

            st.success(
                "Kombucha batch added successfully 🫙"
            )
            st.rerun()

    st.divider()

    rows = get_kombucha_rows()

    if not rows:
        st.info(
            "No kombucha batches yet."
        )
        return

    df = pd.DataFrame(rows)

    df["start_date"] = pd.to_datetime(
        df["start_date"]
    )

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
        "notes",
    ]

    st.dataframe(
        df[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    summary = get_kombucha_summary(
        rows
    )

    st.metric(
        "Active Batches",
        summary["active_count"],
    )

    oldest_batch = summary[
        "oldest_batch"
    ]

    if oldest_batch:
        st.info(
            f'Oldest Active Batch: '
            f'{oldest_batch["batch_name"]} '
            f'({oldest_batch["fermentation_days"]} days)'
        )

    st.divider()
    st.subheader(
        "Update Batch Status"
    )

    batch_options = {
        (
            f'{row["batch_name"]} | '
            f'Day {row["fermentation_days"]} | '
            f'{row["status"]}'
        ): row["id"]
        for row in rows
    }

    selected_batch = st.selectbox(
        "Choose batch",
        list(batch_options.keys()),
    )

    new_status = st.selectbox(
        "New Status",
        [
            "Active",
            "Finished",
            "Discarded",
        ],
    )

    if st.button(
        "Update Status",
        use_container_width=True,
    ):
        update_kombucha_status(
            batch_options[selected_batch],
            new_status,
        )

        st.success(
            "Batch status updated."
        )
        st.rerun()