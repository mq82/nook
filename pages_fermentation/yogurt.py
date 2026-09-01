import streamlit as st
from datetime import time

from utils.time_utils import today_bj_date
from services.fermentation_service import (
    add_yogurt_batch,
    get_yogurt_rows,
    get_yogurt_summary,
    update_yogurt_status,
    delete_yogurt_batch,
)


def render_yogurt():
    st.subheader("Yogurt 🥛")

    with st.form(
        "add_yogurt_form",
        clear_on_submit=True,
    ):
        batch_name = st.text_input(
            "Batch Name"
        )

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=today_bj_date(),
            )
        with col2:
            start_time = st.time_input(
                "Start Time",
                value=time(20, 0),
            )

        milk_type = st.text_input(
            "Milk Type",
            placeholder="Whole milk / Goat milk / Soy milk",
        )

        milk_volume_ml = st.number_input(
            "Milk Volume (ml)",
            min_value=0.0,
            step=100.0,
        )

        col3, col4 = st.columns(2)
        with col3:
            starter_type = st.text_input(
                "Starter Type",
                placeholder="Yogurt / Culture / Previous batch",
            )
        with col4:
            starter_amount = st.text_input(
                "Starter Amount",
                placeholder="2 tbsp / 100 ml / 1 sachet",
            )

        col5, col6 = st.columns(2)
        with col5:
            incubation_temperature_c = st.number_input(
                "Incubation Temperature (°C)",
                min_value=0.0,
                step=1.0,
            )
        with col6:
            incubation_hours = st.number_input(
                "Incubation Time (hours)",
                min_value=0.0,
                step=0.5,
            )

        strained = st.checkbox(
            "Strained"
        )

        yield_ml = st.number_input(
            "Final Yield (ml)",
            min_value=0.0,
            step=100.0,
        )

        notes = st.text_area(
            "Notes"
        )

        submitted = st.form_submit_button(
            "Add Batch",
            use_container_width=True,
        )

        if submitted:
            if not batch_name.strip():
                st.warning(
                    "Please enter batch name."
                )
            else:
                add_yogurt_batch(
                    batch_name=batch_name.strip(),
                    start_date=str(start_date),
                    start_time=start_time.strftime(
                        "%H:%M:%S"
                    ),
                    milk_type=milk_type.strip(),
                    milk_volume_ml=float(
                        milk_volume_ml
                    ),
                    starter_type=starter_type.strip(),
                    starter_amount=starter_amount.strip(),
                    incubation_temperature_c=float(
                        incubation_temperature_c
                    ),
                    incubation_hours=float(
                        incubation_hours
                    ),
                    strained=strained,
                    yield_ml=float(yield_ml),
                    notes=notes.strip(),
                )

                st.success(
                    "Yogurt batch added."
                )
                st.rerun()

    st.divider()

    rows = get_yogurt_rows()
    summary = get_yogurt_summary(rows)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Active Batches",
            summary["active_count"],
        )
    with col2:
        st.metric(
            "Finished Batches",
            summary["finished_count"],
        )

    st.divider()

    if not rows:
        st.info(
            "No yogurt batches yet."
        )
        return

    for row in rows:
        st.markdown(
            f"### {row['batch_name']}"
        )

        details = []

        if row.get("milk_type"):
            details.append(
                row["milk_type"]
            )

        if row.get("milk_volume_ml"):
            details.append(
                f"{row['milk_volume_ml']:g} ml"
            )

        if row.get("incubation_hours"):
            details.append(
                f"{row['incubation_hours']:g} h"
            )

        if details:
            st.caption(
                " · ".join(details)
            )

        start_info = row.get("start_date") or ""

        if row.get("start_time"):
            start_info += (
                f" {row['start_time']}"
            )

        if start_info:
            st.caption(
                f"Started: {start_info}"
            )

        if row.get("starter_type"):
            starter_info = row["starter_type"]

            if row.get("starter_amount"):
                starter_info += (
                    f" · {row['starter_amount']}"
                )

            st.caption(
                f"Starter: {starter_info}"
            )

        if row.get("incubation_temperature_c"):
            st.caption(
                f"Incubation: "
                f"{row['incubation_temperature_c']:g} °C"
            )

        if row.get("strained"):
            st.caption(
                "Strained: Yes"
            )

        if row.get("yield_ml"):
            st.caption(
                f"Final yield: "
                f"{row['yield_ml']:g} ml"
            )

        st.caption(
            f"Status: {row['status']}"
        )

        if row.get("notes"):
            st.caption(
                f"📝 {row['notes']}"
            )

        status_options = [
            "Active",
            "Finished",
            "Discarded",
        ]

        current_status = row["status"]

        if current_status in status_options:
            status_index = status_options.index(
                current_status
            )
        else:
            status_index = 0

        new_status = st.selectbox(
            "Status",
            status_options,
            index=status_index,
            key=f"yogurt_status_{row['id']}",
        )

        col7, col8 = st.columns(2)
        with col7:
            if st.button(
                "Update Status",
                key=f"update_yogurt_{row['id']}",
                use_container_width=True,
            ):
                update_yogurt_status(
                    row["id"],
                    new_status,
                )

                st.success(
                    "Status updated."
                )
                st.rerun()

        with col8:
            if st.button(
                "Delete",
                key=f"delete_yogurt_{row['id']}",
                use_container_width=True,
            ):
                delete_yogurt_batch(
                    row["id"]
                )

                st.success(
                    "Batch deleted."
                )
                st.rerun()

        st.divider()