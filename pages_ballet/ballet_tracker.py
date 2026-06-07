import sys
from pathlib import Path

import streamlit as st
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from utils.supabase_client import get_supabase_client

def delete_ballet_class(class_id):
    supabase = get_supabase_client()

    return (
        supabase
        .table("ballet_classes")
        .delete()
        .eq("id", class_id)
        .execute()
    )

def update_ballet_class(class_id, data):
    supabase = get_supabase_client()

    return (
        supabase
        .table("ballet_classes")
        .update(data)
        .eq("id", class_id)
        .execute()
    )

def render_ballet_tracker():
    st.subheader("Ballet Class Tracker 🩰")

    supabase = get_supabase_client()

    with st.form("add_ballet_class_form", clear_on_submit=True):
        class_date = st.date_input("Class Date")
        start_time = st.time_input("Start Time")
        duration_hours = st.number_input(
            "Duration (hours)",
            min_value=0.5,
            step=0.5,
            value=1.5
        )

        city = st.text_input("City")
        studio = st.text_input("Studio / Institution")
        address = st.text_input("Address")
        teacher = st.text_input("Teacher")

        class_type = st.selectbox(
            "Class Type",
            ["Ballet", "Pointe", "Floor Barre", "Pilates", "Other"]
        )

        level = st.selectbox(
            "Level",
            ["Beginner", "Basic", "Intermediate", "Open Class", "Other"]
        )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Class")

        if submitted:
            data = {
                "class_date": str(class_date),
                "start_time": str(start_time),
                "duration_hours": float(duration_hours),
                "city": city.strip(),
                "studio": studio.strip(),
                "address": address.strip(),
                "teacher": teacher.strip(),
                "class_type": class_type,
                "level": level,
                "notes": notes.strip(),
            }

            supabase.table("ballet_classes").insert(data).execute()
            st.success("Ballet class added successfully 🩰")
   
    st.divider()

    result = (
        supabase
        .table("ballet_classes")
        .select("*")
        .order("class_date", desc=True)
        .execute()
    )

    records = result.data

    if not records:
        st.info("No ballet classes recorded yet.")
        return
    
    df = pd.DataFrame(records)
    df["class_date"] = pd.to_datetime(df["class_date"])

    st.subheader("Filters")

    min_date = df["class_date"].min().date()
    max_date = df["class_date"].max().date()

    col1, col2 = st.columns(2)

    with col1:
        start_filter = st.date_input("From", value=min_date)
    
    with col2:
        end_filter = st.date_input("To", value=max_date)

    city_options = ["All"] + sorted(df["city"].dropna().unique().tolist())
    teacher_options = ["All"] + sorted(df["teacher"].dropna().unique().tolist())
    studio_options = ["All"] + sorted(df["studio"].dropna().unique().tolist())

    col3, col4, col5 = st.columns(3)

    with col3:
        city_filter = st.selectbox("City", city_options)
    
    with col4:
        teacher_filter = st.selectbox("Teacher", teacher_options)
    
    with col5:
        studio_filter = st.selectbox("Studio", studio_options)

    filtered_df = df[
        (df["class_date"].dt.date >= start_filter) &
        (df["class_date"].dt.date <= end_filter)
    ]

    if city_filter != "All":
        filtered_df = filtered_df[filtered_df["city"] == city_filter]

    if teacher_filter != "All":
        filtered_df = filtered_df[filtered_df["teacher"] == teacher_filter]

    if studio_filter != "All":
        filtered_df = filtered_df[filtered_df["studio"] == studio_filter]

    st.divider()

    st.subheader("Summary")

    total_hours = filtered_df["duration_hours"].sum()
    total_classes = len(filtered_df)

    col6, col7 = st.columns(2)

    with col6:
        st.metric("Total Classes", total_classes)

    with col7:
        st.metric("Total Hours", f"{total_hours:.1f} hrs")

    st.divider()

    st.subheader("Class History")

    display_columns = [
        "class_date",
        "start_time",
        "duration_hours",
        "city",
        "studio",
        "teacher",
        "class_type",
        "level",
        "notes"
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("Remove Class")

    class_options = {
        f'{row["class_date"].date()} | {row["start_time"]} | {row["studio"]} | {row["teacher"]}': row["id"]
        for _, row in filtered_df.iterrows()
    }

    if class_options:
        selected_class = st.selectbox(
            "Choose class to remove",
            list(class_options.keys())
        )

        if st.button("Remove Selected Class", use_container_width=True):
            delete_ballet_class(class_options[selected_class])
            st.success("Class removed.")
            st.rerun()

    st.divider()
    st.subheader("Edit Class")

    edit_options = {
        f'{row["class_date"].date()} | {row["start_time"]} | {row["studio"]} | {row["teacher"]}': row["id"]
        for _, row in filtered_df.iterrows()
    }

    if edit_options:
        selected_edit_label = st.selectbox(
            "Choose class to edit",
            list(edit_options.keys())
        )

        selected_edit_id = edit_options[selected_edit_label]

        selected_row = filtered_df[
            filtered_df["id"] == selected_edit_id
        ].iloc[0]

        with st.form("edit_ballet_class_form"):
            edit_date = st.date_input(
                "Class Date",
                value=selected_row["class_date"].date()
            )

            edit_start_time = st.time_input(
                "Start Time",
                value=pd.to_datetime(str(selected_row["start_time"])).time()
            )

            edit_duration_hours = st.number_input(
                "Duration Hours",
                min_value=0.5,
                step=0.5,
                value=float(selected_row["duration_hours"])
            )

            edit_city = st.text_input(
                "City",
                value=selected_row["city"] or ""
            )

            edit_studio = st.text_input(
                "Studio / Institution",
                value=selected_row["studio"] or ""
            )

            edit_address = st.text_input(
                "Address",
                value=selected_row["address"] or ""
            )

            edit_teacher = st.text_input(
                "Teacher",
                value=selected_row["teacher"] or ""
            )

            edit_class_type = st.selectbox(
                "Class Type",
                ["Ballet", "Pointe", "Floor Barre", "Pilates", "Other"],
                index=["Ballet", "Pointe", "Floor Barre", "Pilates", "Other"].index(
                    selected_row["class_type"]
                ) if selected_row["class_type"] in ["Ballet", "Pointe", "Floor Barre", "Pilates", "Other"] else 0
            )

            edit_level = st.selectbox(
                "Level",
                ["Beginner", "Basic", "Intermediate", "Open Class", "Other"],
                index=["Beginner", "Basic", "Intermediate", "Open Class", "Other"].index(
                    selected_row["level"]
                ) if selected_row["level"] in ["Beginner", "Basic", "Intermediate", "Open Class", "Other"] else 0
            )

            edit_notes = st.text_area(
                "Notes",
                value=selected_row["notes"] or ""
            )

            submitted_edit = st.form_submit_button(
                "Save Changes",
                use_container_width=True
            )

            if submitted_edit:
                update_ballet_class(
                    selected_edit_id,
                    {
                        "class_date": str(edit_date),
                        "start_time": str(edit_start_time),
                        "duration_hours": float(edit_duration_hours),
                        "city": edit_city.strip(),
                        "studio": edit_studio.strip(),
                        "address": edit_address.strip(),
                        "teacher": edit_teacher.strip(),
                        "class_type": edit_class_type,
                        "level": edit_level,
                        "notes": edit_notes.strip(),
                    }
                )

                st.success("Class updated.")
                st.rerun()

    st.subheader("Status")

    city_hours = (
        filtered_df
        .groupby("city", dropna=False)["duration_hours"]
        .sum()
        .reset_index()
        .sort_values("duration_hours", ascending=False)
    )

    teacher_hours = (
        filtered_df
        .groupby("teacher", dropna=False)["duration_hours"]
        .sum()
        .reset_index()
        .sort_values("duration_hours", ascending=False)
    )

    col8, col9 = st.columns(2)

    with col8:
        st.write("Hours by City")
        st.dataframe(
            city_hours,
            use_container_width=True,
            hide_index=True
        )
    
    with col9:
        st.write("Hours by Teacher")
        st.dataframe(
            teacher_hours,
            use_container_width=True,
            hide_index=True
        )
