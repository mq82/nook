import streamlit as st
import pandas as pd
from datetime import date

from services.period_service import (
    save_period_record,
    get_period_history_dataframe,
    get_period_summary,
    update_period_record,
    delete_period_record,
    save_daily_log,
    get_daily_logs_dataframe,
    update_daily_log,
    delete_daily_log,
    import_period_records,
)


FLOW_LEVELS = [
    "",
    "Light",
    "Medium",
    "Heavy",
]

MOOD_OPTIONS = [
    "Good",
    "Happy",
    "Sad",
    "Irritable",
    "Anxious",
    "Neutral",
]


def render_period_tracker():
    st.subheader("Period Tracker")

    page = st.segmented_control(
        "Choose Section",
        [
            "Add Period",
            "Period History",
            "Daily Log",
            "Import CSV",
        ],
        default="Add Period",
    )

    if page == "Add Period":
        render_add_period()

    elif page == "Period History":
        render_period_history()

    elif page == "Daily Log":
        render_daily_log()

    elif page == "Import CSV":
        render_import_csv()


# ---------- Add Period ----------

def render_add_period():
    st.markdown("### Add Period Record")

    start_date = st.date_input(
        "Start Date",
        value=date.today(),
    )

    end_date = st.date_input(
        "End Date",
        value=None,
    )

    flow_level = st.selectbox(
        "Flow Level",
        FLOW_LEVELS,
    )

    notes = st.text_area("Notes")

    if st.button(
        "Save Period",
        use_container_width=True,
    ):
        save_period_record(
            start_date=start_date,
            end_date=end_date,
            flow_level=flow_level,
            notes=notes,
        )

        st.success("Period record saved.")
        st.rerun()


# ---------- Period History ----------

def render_period_history():
    st.markdown("### Period History")

    df = get_period_history_dataframe()

    if df.empty:
        st.info("No period records yet.")
        return

    summary = get_period_summary(df)

    col1, col2 = st.columns(2)

    with col1:
        if summary["avg_cycle_length"] is not None:
            st.metric(
                "Avg Cycle Length",
                f'{summary["avg_cycle_length"]:.1f} days',
            )
        else:
            st.metric(
                "Avg Cycle Length",
                "-",
            )

    with col2:
        if summary["avg_period_length"] is not None:
            st.metric(
                "Avg Period Length",
                f'{summary["avg_period_length"]:.1f} days',
            )
        else:
            st.metric(
                "Avg Period Length",
                "-",
            )

    if (
        summary["current_cycle_day"] is not None
        and summary["latest_start"] is not None
    ):
        st.info(
            f'Current cycle: '
            f'Day {summary["current_cycle_day"]} '
            f'(started on {summary["latest_start"]})'
        )

    display_columns = [
        "start_date",
        "end_date",
        "period_length_days",
        "cycle_length_days",
        "flow_level",
        "source",
        "notes",
    ]

    st.dataframe(
        df[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Delete Period Record")

    record_options = {
        (
            f'{row["start_date"].date()} → '
            f'{row["end_date"].date() if pd.notna(row["end_date"]) else ""} | '
            f'{row.get("flow_level") or ""}'
        ): row["id"]
        for _, row in df.iterrows()
    }

    selected_record = st.selectbox(
        "Choose record to delete",
        list(record_options.keys()),
    )

    if st.button(
        "Delete Selected Period Record",
        use_container_width=True,
    ):
        delete_period_record(
            record_options[selected_record]
        )

        st.success("Period record deleted.")
        st.rerun()

    st.divider()
    st.subheader("Edit Period Record")

    edit_options = {
        (
            f'{row["start_date"].date()} → '
            f'{row["end_date"].date() if pd.notna(row["end_date"]) else ""} | '
            f'{row.get("flow_level") or ""}'
        ): row["id"]
        for _, row in df.iterrows()
    }

    selected_edit = st.selectbox(
        "Choose record to edit",
        list(edit_options.keys()),
    )

    selected_edit_id = edit_options[
        selected_edit
    ]

    selected_row = df[
        df["id"] == selected_edit_id
    ].iloc[0]

    current_flow_level = (
        selected_row["flow_level"]
        if selected_row["flow_level"] in FLOW_LEVELS
        else ""
    )

    with st.form("edit_period_form"):
        edit_start_date = st.date_input(
            "Start Date",
            value=selected_row["start_date"].date(),
        )

        edit_end_date = st.date_input(
            "End Date",
            value=(
                selected_row["end_date"].date()
                if pd.notna(selected_row["end_date"])
                else None
            ),
        )

        edit_flow_level = st.selectbox(
            "Flow Level",
            FLOW_LEVELS,
            index=FLOW_LEVELS.index(
                current_flow_level
            ),
        )

        edit_notes = st.text_area(
            "Notes",
            value=selected_row["notes"] or "",
        )

        submitted_edit = st.form_submit_button(
            "Save Period Changes",
            use_container_width=True,
        )

        if submitted_edit:
            update_period_record(
                selected_edit_id,
                {
                    "start_date": str(edit_start_date),
                    "end_date": (
                        str(edit_end_date)
                        if edit_end_date
                        else None
                    ),
                    "flow_level": (
                        edit_flow_level
                        or None
                    ),
                    "notes": (
                        edit_notes
                        or None
                    ),
                },
            )

            st.success("Period record updated.")
            st.rerun()


# ---------- Daily Log ----------

def render_daily_log():
    st.markdown("### Daily Check-in")

    with st.form(
        "period_daily_log_form",
        clear_on_submit=True,
    ):
        log_date = st.date_input(
            "Date",
            value=date.today(),
        )

        sleep_hours = st.number_input(
            "Sleep Hours",
            min_value=0.0,
            max_value=24.0,
            step=0.5,
        )

        energy_level = st.slider(
            "Energy Level",
            1,
            10,
            5,
        )

        stress_level = st.slider(
            "Stress Level",
            1,
            10,
            5,
        )

        mood = st.selectbox(
            "Mood",
            MOOD_OPTIONS,
        )

        lower_ab_pain = st.slider(
            "Lower Abdomen Pain",
            0,
            10,
            0,
        )

        notes = st.text_area(
            "Additional Notes"
        )

        submitted = st.form_submit_button(
            "Save Daily Log",
            use_container_width=True,
        )

    if submitted:
        save_daily_log(
            log_date=log_date,
            sleep_hours=sleep_hours,
            energy_level=energy_level,
            stress_level=stress_level,
            mood=mood,
            lower_ab_pain=lower_ab_pain,
            notes=notes,
        )

        st.success("Daily log saved.")
        st.rerun()

    st.divider()
    st.markdown("### Recent Daily Logs")

    daily_df = get_daily_logs_dataframe(
        limit=30
    )

    if daily_df.empty:
        st.info("No daily logs yet.")
        return

    st.dataframe(
        daily_df,
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Delete Daily Log")

    log_options = {
        (
            f'{row["log_date"]} | '
            f'mood={row.get("mood") or ""} | '
            f'pain={row.get("lower_ab_pain") or 0}'
        ): row["id"]
        for _, row in daily_df.iterrows()
    }

    selected_log = st.selectbox(
        "Choose daily log to delete",
        list(log_options.keys()),
    )

    if st.button(
        "Delete Selected Daily Log",
        use_container_width=True,
    ):
        delete_daily_log(
            log_options[selected_log]
        )

        st.success("Daily log deleted.")
        st.rerun()

    st.divider()
    st.subheader("Edit Daily Log")

    edit_log_options = {
        (
            f'{row["log_date"]} | '
            f'mood={row.get("mood") or ""} | '
            f'pain={row.get("lower_ab_pain") or 0}'
        ): row["id"]
        for _, row in daily_df.iterrows()
    }

    selected_edit_log = st.selectbox(
        "Choose daily log to edit",
        list(edit_log_options.keys()),
    )

    selected_edit_log_id = edit_log_options[
        selected_edit_log
    ]

    selected_log_row = daily_df[
        daily_df["id"] == selected_edit_log_id
    ].iloc[0]

    current_mood = (
        selected_log_row["mood"]
        if selected_log_row["mood"] in MOOD_OPTIONS
        else MOOD_OPTIONS[0]
    )

    with st.form("edit_daily_log_form"):
        edit_log_date = st.date_input(
            "Date",
            value=pd.to_datetime(
                selected_log_row["log_date"]
            ).date(),
        )

        edit_sleep_hours = st.number_input(
            "Sleep Hours",
            min_value=0.0,
            max_value=24.0,
            step=0.5,
            value=float(
                selected_log_row["sleep_hours"]
                or 0
            ),
        )

        edit_energy_level = st.slider(
            "Energy Level",
            1,
            10,
            int(
                selected_log_row["energy_level"]
                or 5
            ),
        )

        edit_stress_level = st.slider(
            "Stress Level",
            1,
            10,
            int(
                selected_log_row["stress_level"]
                or 5
            ),
        )

        edit_mood = st.selectbox(
            "Mood",
            MOOD_OPTIONS,
            index=MOOD_OPTIONS.index(
                current_mood
            ),
        )

        edit_lower_ab_pain = st.slider(
            "Lower Abdomen Pain",
            0,
            10,
            int(
                selected_log_row["lower_ab_pain"]
                or 0
            ),
        )

        edit_notes = st.text_area(
            "Additional Notes",
            value=selected_log_row["notes"] or "",
        )

        submitted_edit_log = st.form_submit_button(
            "Save Daily Log Changes",
            use_container_width=True,
        )

        if submitted_edit_log:
            update_daily_log(
                selected_edit_log_id,
                {
                    "log_date": str(edit_log_date),
                    "sleep_hours": edit_sleep_hours,
                    "energy_level": edit_energy_level,
                    "stress_level": edit_stress_level,
                    "mood": edit_mood,
                    "lower_ab_pain": edit_lower_ab_pain,
                    "notes": (
                        edit_notes
                        or None
                    ),
                },
            )

            st.success("Daily log updated.")
            st.rerun()


# ---------- CSV Import ----------

def render_import_csv():
    st.markdown("### Import Period CSV")

    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=["csv"],
    )

    if uploaded_file is None:
        return

    df = pd.read_csv(uploaded_file)

    st.write(
        "Preview of uploaded data:"
    )

    st.dataframe(
        df.head(20),
        use_container_width=True,
        hide_index=True,
    )

    if st.button(
        "Import CSV Data",
        use_container_width=True,
    ):
        try:
            imported_count = import_period_records(
                df
            )

            if imported_count == 0:
                st.warning(
                    "No valid records found in the CSV."
                )
            else:
                st.success(
                    f"Successfully imported "
                    f"{imported_count} period records."
                )

        except Exception as e:
            st.error(
                f"Import failed: {e}"
            )