import streamlit as st
from utils.home_db import (
    add_supplement_log,
    delete_supplement_log,
    get_supplement_logs_by_date,
    get_supplement_daily_summary,
)

from utils.master_data import get_option_labels

def render_vera_supplements():
    st.subheader("Vera Supplements Log")

    st.caption("Record what you take at the current time. No manual date/time input.")

    with st.form("add_supplement_form", clear_on_submit=True):
        common_supplements = get_option_labels("supplements")

        selected_supplement = st.selectbox(
            "Supplement Name",
            common_supplements
        )

        if selected_supplement == "Other":
            supplement_name = st.text_input(
                "Custom Supplement Name"
            )
        else:
            supplement_name = selected_supplement

        col1, col2 = st.columns(2)

        with col1:
            dosage = st.number_input(
                "Dosage",
                min_value=0.0,
                step=1.0
            )

        with col2:
            unit = st.selectbox(
                "Unit",
                [
                    "capsule(s)",
                    "tablet(s)",
                    "drop(s)",
                    "mg",
                    "g",
                    "IU",
                    "mcg"
                ]
            )

        note = st.text_area(
            "Note",
            placeholder="Optional: after lunch, felt dizzy, with food, etc."
        )

        submitted = st.form_submit_button("Add Log", use_container_width=True)

        if submitted:
            if supplement_name.strip():
                add_supplement_log(
                    supplement_name.strip(),
                    dosage,
                    unit,
                    note.strip()
                )
                st.success("Supplement log added.")
                st.rerun()
            else:
                st.warning("Please enter a supplement name.")

    st.divider()

    selected_supplement_date = st.date_input("Select Date")
    selected_date_str = str(selected_supplement_date)

    st.markdown(f"### Daily Summary - {selected_date_str}")

    summary = get_supplement_daily_summary(selected_date_str)

    if not summary:
        st.caption("No supplements recorded on this date.")
    else:
        for item in summary:
            st.markdown(
                f"- **{item['supplement_name']}**: "
                f"{item['total_dosage']} {item['unit']}"
            )

    st.divider()

    st.markdown(f"### Logs - {selected_date_str}")

    logs = get_supplement_logs_by_date(selected_date_str)

    supplement_filter_options = ["All"] + sorted(
        list(set(log["supplement_name"] for log in logs))
    ) if logs else ["All"]

    selected_filter = st.selectbox(
        "Filter by Supplement",
        supplement_filter_options
    )

    if selected_filter != "All":
        logs = [
            log for log in logs
            if log["supplement_name"] == selected_filter
        ]

    if not logs:
        st.caption("No supplement logs for this date.")
    else:
        for log in logs:
            col1, col2 = st.columns([6, 1.5])

            with col1:
                st.markdown(
                    f"### {log['supplement_name']} - {log['dosage']} {log['unit']}"
                )
                st.caption(f"Taken at: {log['taken_at']}")

                if log["note"]:
                    st.caption(f"Note: {log['note']}")

            with col2:
                if st.button(
                    "Delete",
                    key=f"delete_log_{log['id']}",
                    use_container_width=True
                ):
                    delete_supplement_log(log["id"])
                    st.success("Deleted one log.")
                    st.rerun()

            st.divider()