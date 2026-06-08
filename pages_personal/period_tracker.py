import streamlit as st
import pandas as pd
from datetime import date
from utils.supabase_client import get_supabase_client


def clean_period_csv(df):
    df = df.copy()

    # normalize column names
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    required_columns = ["start_date", "end_date"]

    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce").dt.date
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce").dt.date

    if "flow_level" not in df.columns:
        df["flow_level"] = None

    if "notes" not in df.columns:
        df["notes"] = None

    df = df.dropna(subset=["start_date"])
    df = df.drop_duplicates(subset=["start_date"])

    records = []

    for _, row in df.iterrows():
        records.append({
            "start_date": str(row["start_date"]),
            "end_date": str(row["end_date"]) if pd.notna(row["end_date"]) else None,
            "flow_level": row["flow_level"] if pd.notna(row["flow_level"]) else None,
            "source": "csv_import",
            "notes": row["notes"] if pd.notna(row["notes"]) else None,
        })

    return records

def delete_period_record(record_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("cycle_periods")
        .delete()
        .eq("id", record_id)
        .execute()
    )

def update_period_record(record_id, data):
    supabase = get_supabase_client()

    return (
        supabase
        .table("cycle_periods")
        .update(data)
        .eq("id", record_id)
        .execute()
    )

def update_daily_log(log_id, data):
    supabase = get_supabase_client()

    return (
        supabase
        .table("daily_logs")
        .update(data)
        .eq("id", log_id)
        .execute()
    )


def delete_daily_log(log_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("daily_logs")
        .delete()
        .eq("id", log_id)
        .execute()
    )

def render_period_tracker():
    st.subheader("Period Tracker")

    supabase = get_supabase_client()

    page = st.segmented_control(
        "Choose Section",
        [
            "Add Period",
            "Period History",
            "Daily Log",
            "Import CSV"
        ],
        default="Add Period"
    )

    if page == "Add Period":
        st.markdown("### Add Period Record")

        start_date = st.date_input("Start Date", value=date.today())
        end_date = st.date_input("End Date", value=None)
        flow_level = st.selectbox("Flow Level", ["", "Light", "Medium", "Heavy"])
        notes = st.text_area("Notes")

        if st.button("Save Period", use_container_width=True):
            data = {
                "start_date": str(start_date),
                "end_date": str(end_date) if end_date else None,
                "flow_level": flow_level or None,
                "source": "manual",
                "notes": notes or None,
            }

            supabase.table("cycle_periods").upsert(
                data,
                on_conflict="start_date"
            ).execute()

            st.success("Period record saved.")

    elif page == "Period History":
        st.markdown("### Period History")

        response = (
            supabase
            .table("cycle_periods")
            .select("*")
            .order("start_date", desc=True)
            .execute()
        )

        records = response.data

        if not records:
            st.info("No period records yet.")
        else:
            df = pd.DataFrame(records)
            df["start_date"] = pd.to_datetime(df["start_date"])
            df["end_date"] = pd.to_datetime(df["end_date"])

            df = df.sort_values("start_date", ascending=False)

            df["period_length_days"] = (
                df["end_date"] - df["start_date"]
            ).dt.days + 1

            df_sorted_asc = df.sort_values("start_date")
            df_sorted_asc["cycle_length_days"] = (
                df_sorted_asc["start_date"]
                .diff()
                .dt.days
            )

            recent_cycle_lengths = (
                df_sorted_asc["cycle_length_days"]
                .dropna()
                .tail(6)
            )

            col1, col2 = st.columns(2)

            with col1:
                if not recent_cycle_lengths.empty:
                    st.metric(
                        "Avg Cycle Length",
                        f"{recent_cycle_lengths.mean():.1f} days"
                    )
                else:
                    st.metric("Avg Cycle Length", "-")

            with col2:
                recent_period_lengths = (
                    df["period_length_days"]
                    .dropna()
                    .head(6)
                )

                if not recent_period_lengths.empty:
                    st.metric(
                        "Avg Period Length",
                        f"{recent_period_lengths.mean():.1f} days"
                    )
                else:
                    st.metric("Avg Period Length", "-")

            latest_record = df.sort_values("start_date", ascending=False).iloc[0]
            latest_start = latest_record["start_date"].date()
            current_cycle_day = (date.today() - latest_start).days + 1

            st.info(
                f"Current cycle: Day {current_cycle_day} "
                f"(started on {latest_start})"
            )

            st.dataframe(df, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Delete Period Record")

            record_options = {
                f'{row["start_date"]} → {row.get("end_date") or ""} | {row.get("flow_level") or ""}': row["id"]
                for _, row in df.iterrows()
            }

            selected_record = st.selectbox(
                "Choose record to delete",
                list(record_options.keys())
            )

            if st.button("Delete Selected Period Record", use_container_width=True):
                delete_period_record(record_options[selected_record])
                st.success("Period record deleted.")
                st.rerun()

            st.divider()
            st.subheader("Edit Period Record")

            edit_options = {
                f'{row["start_date"].date()} → {row["end_date"].date() if pd.notna(row["end_date"]) else ""} | {row.get("flow_level") or ""}': row["id"]
                for _, row in df.iterrows()
            }

            selected_edit = st.selectbox(
                "Choose record to edit",
                list(edit_options.keys())
            )

            selected_edit_id = edit_options[selected_edit]
            selected_row = df[df["id"] == selected_edit_id].iloc[0]

            with st.form("edit_period_form"):
                edit_start_date = st.date_input(
                    "Start Date",
                    value=selected_row["start_date"].date()
                )

                edit_end_date = st.date_input(
                    "End Date",
                    value=selected_row["end_date"].date() if pd.notna(selected_row["end_date"]) else date.today()
                )

                edit_flow_level = st.selectbox(
                    "Flow Level",
                    ["", "Light", "Medium", "Heavy"],
                    index=["", "Light", "Medium", "Heavy"].index(
                        selected_row["flow_level"]
                    ) if selected_row["flow_level"] in ["", "Light", "Medium", "Heavy"] else 0
                )

                edit_notes = st.text_area(
                    "Notes",
                    value=selected_row["notes"] or ""
                )

                submitted_edit = st.form_submit_button(
                    "Save Period Changes",
                    use_container_width=True
                )

                if submitted_edit:
                    update_period_record(
                        selected_edit_id,
                        {
                            "start_date": str(edit_start_date),
                            "end_date": str(edit_end_date),
                            "flow_level": edit_flow_level or None,
                            "notes": edit_notes or None,
                        }
                    )

                    st.success("Period record updated.")
                    st.rerun()

    elif page == "Daily Log":
        st.markdown("### Daily Check-in")

        with st.form("period_daily_log_form", clear_on_submit=True):
            log_date = st.date_input("Date", value=date.today())

            sleep_hours = st.number_input(
                "Sleep Hours",
                min_value=0.0,
                max_value=24.0,
                step=0.5
            )

            energy_level = st.slider("Energy Level", 1, 10, 5)
            stress_level = st.slider("Stress Level", 1, 10, 5)

            mood = st.selectbox(
                "Mood",
                [
                    "Good",
                    "Happy",
                    "Sad",
                    "Irritable",
                    "Anxious",
                    "Neutral"
                ]
            )

            lower_ab_pain = st.slider("Lower Abdomen Pain", 0, 10, 0)
            notes = st.text_area("Additional Notes")

            submitted = st.form_submit_button("Save Daily Log", use_container_width=True)

        if submitted:
            log_data = {
                "log_date": str(log_date),
                "sleep_hours": sleep_hours,
                "energy_level": energy_level,
                "stress_level": stress_level,
                "mood": mood,
                "lower_ab_pain": lower_ab_pain,
                "notes": notes or None,
            }

            (
                supabase
                .table("daily_logs")
                .upsert(
                    log_data,
                    on_conflict="log_date"
                )
                .execute()
            )

            st.success("Daily log saved.")

        st.divider()
        st.markdown("### Recent Daily Logs")

        response = (
            supabase
            .table("daily_logs")
            .select("*")
            .order("log_date", desc=True)
            .limit(30)
            .execute()
        )

        if response.data:
            daily_df = pd.DataFrame(response.data)
            st.dataframe(daily_df, use_container_width=True, hide_index=True)

            st.divider()
            st.subheader("Delete Daily Log")

            log_options = {
                f'{row["log_date"]} | mood={row.get("mood") or ""} | pain={row.get("lower_ab_pain") or 0}': row["id"]
                for _, row in daily_df.iterrows()
            }

            selected_log = st.selectbox(
                "Choose daily log to delete",
                list(log_options.keys())
            )

            if st.button("Delete Selected Daily Log", use_container_width=True):
                delete_daily_log(log_options[selected_log])
                st.success("Daily log deleted.")
                st.rerun()
            st.divider()
            st.subheader("Edit Daily Log")

            edit_log_options = {
                f'{row["log_date"]} | mood={row.get("mood") or ""} | pain={row.get("lower_ab_pain") or 0}': row["id"]
                for _, row in daily_df.iterrows()
            }

            selected_edit_log = st.selectbox(
                "Choose daily log to edit",
                list(edit_log_options.keys())
            )

            selected_edit_log_id = edit_log_options[selected_edit_log]
            selected_log_row = daily_df[
                daily_df["id"] == selected_edit_log_id
            ].iloc[0]

            with st.form("edit_daily_log_form"):
                edit_log_date = st.date_input(
                    "Date",
                    value=pd.to_datetime(selected_log_row["log_date"]).date()
                )

                edit_sleep_hours = st.number_input(
                    "Sleep Hours",
                    min_value=0.0,
                    max_value=24.0,
                    step=0.5,
                    value=float(selected_log_row["sleep_hours"] or 0)
                )

                edit_energy_level = st.slider(
                    "Energy Level",
                    1,
                    10,
                    int(selected_log_row["energy_level"] or 5)
                )

                edit_stress_level = st.slider(
                    "Stress Level",
                    1,
                    10,
                    int(selected_log_row["stress_level"] or 5)
                )

                mood_options = [
                    "Good",
                    "Happy",
                    "Sad",
                    "Irritable",
                    "Anxious",
                    "Neutral"
                ]

                edit_mood = st.selectbox(
                    "Mood",
                    mood_options,
                    index=mood_options.index(selected_log_row["mood"])
                    if selected_log_row["mood"] in mood_options else 0
                )

                edit_lower_ab_pain = st.slider(
                    "Lower Abdomen Pain",
                    0,
                    10,
                    int(selected_log_row["lower_ab_pain"] or 0)
                )

                edit_notes = st.text_area(
                    "Additional Notes",
                    value=selected_log_row["notes"] or ""
                )

                submitted_edit_log = st.form_submit_button(
                    "Save Daily Log Changes",
                    use_container_width=True
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
                            "notes": edit_notes or None,
                        }
                    )

                    st.success("Daily log updated.")
                    st.rerun()
        else:
            st.info("No daily logs yet.")


    elif page == "Import CSV":
        st.markdown("### Import Period CSV")

        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("Preview of uploaded data:")
            st.dataframe(df.head(20), use_container_width=True)

            if st.button("Import CSV Data", use_container_width=True):
                try:
                    records = clean_period_csv(df)

                    if len(records) == 0:
                        st.warning("No valid records found in the CSV.")
                    else:
                        supabase.table("cycle_periods").upsert(
                            records,
                            on_conflict="start_date"
                        ).execute()

                        st.success(f"Successfully imported {len(records)} period records.")

                except Exception as e:
                    st.error(f"Import failed: {e}")