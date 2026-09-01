import streamlit as st
import pandas as pd

from services.ballet_service import (
    add_ballet_class,
    get_ballet_dataframe,
    get_filter_options,
    filter_ballet_classes,
    get_ballet_summary,
    get_ballet_status_tables,
    update_ballet_class,
    delete_ballet_class,
)


CLASS_TYPES = [
    "Ballet",
    "Pointe",
    "Floor Barre",
    "Pilates",
    "Other",
]

LEVELS = [
    "Beginner",
    "Basic",
    "Intermediate",
    "Open Class",
    "Other",
]


def render_ballet_tracker():
    st.subheader("Ballet Class Tracker 🩰")

    with st.form(
        "add_ballet_class_form",
        clear_on_submit=True,
    ):
        class_date = st.date_input(
            "Class Date"
        )

        start_time = st.time_input(
            "Start Time"
        )

        duration_hours = st.number_input(
            "Duration (hours)",
            min_value=0.5,
            step=0.5,
            value=1.5,
        )

        city = st.text_input(
            "City"
        )

        studio = st.text_input(
            "Studio / Institution"
        )

        address = st.text_input(
            "Address"
        )

        teacher = st.text_input(
            "Teacher"
        )

        class_type = st.selectbox(
            "Class Type",
            CLASS_TYPES,
        )

        level = st.selectbox(
            "Level",
            LEVELS,
        )

        notes = st.text_area(
            "Notes"
        )

        submitted = st.form_submit_button(
            "Add Class"
        )

        if submitted:
            add_ballet_class(
                class_date=str(class_date),
                start_time=str(start_time),
                duration_hours=float(duration_hours),
                city=city.strip(),
                studio=studio.strip(),
                address=address.strip(),
                teacher=teacher.strip(),
                class_type=class_type,
                level=level,
                notes=notes.strip(),
            )

            st.success(
                "Ballet class added successfully 🩰"
            )
            st.rerun()

    st.divider()

    df = get_ballet_dataframe()

    if df.empty:
        st.info(
            "No ballet classes recorded yet."
        )
        return

    st.subheader("Filters")

    filter_options = get_filter_options(
        df
    )

    col1, col2 = st.columns(2)
    with col1:
        start_filter = st.date_input(
            "From",
            value=filter_options["min_date"],
        )
    with col2:
        end_filter = st.date_input(
            "To",
            value=filter_options["max_date"],
        )

    col3, col4, col5 = st.columns(3)
    with col3:
        city_filter = st.selectbox(
            "City",
            filter_options["cities"],
        )
    with col4:
        teacher_filter = st.selectbox(
            "Teacher",
            filter_options["teachers"],
        )
    with col5:
        studio_filter = st.selectbox(
            "Studio",
            filter_options["studios"],
        )

    filtered_df = filter_ballet_classes(
        df=df,
        start_date=start_filter,
        end_date=end_filter,
        city=city_filter,
        teacher=teacher_filter,
        studio=studio_filter,
    )

    st.divider()
    st.subheader("Summary")

    summary = get_ballet_summary(
        filtered_df
    )

    col6, col7 = st.columns(2)
    with col6:
        st.metric(
            "Total Classes",
            summary["total_classes"],
        )
    with col7:
        st.metric(
            "Total Hours",
            f'{summary["total_hours"]:.1f} hrs',
        )

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
        "notes",
    ]

    st.dataframe(
        filtered_df[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.subheader("Remove Class")

    class_options = {
        (
            f'{row["class_date"].date()} | '
            f'{row["start_time"]} | '
            f'{row["studio"] or ""} | '
            f'{row["teacher"] or ""}'
        ): row["id"]
        for _, row in filtered_df.iterrows()
    }

    if class_options:
        selected_class = st.selectbox(
            "Choose class to remove",
            list(class_options.keys()),
        )

        if st.button(
            "Remove Selected Class",
            use_container_width=True,
        ):
            delete_ballet_class(
                class_options[selected_class]
            )

            st.success(
                "Class removed."
            )
            st.rerun()

    st.divider()
    st.subheader("Edit Class")

    edit_options = {
        (
            f'{row["class_date"].date()} | '
            f'{row["start_time"]} | '
            f'{row["studio"] or ""} | '
            f'{row["teacher"] or ""}'
        ): row["id"]
        for _, row in filtered_df.iterrows()
    }

    if edit_options:
        selected_edit_label = st.selectbox(
            "Choose class to edit",
            list(edit_options.keys()),
        )

        selected_edit_id = edit_options[
            selected_edit_label
        ]

        selected_row = filtered_df[
            filtered_df["id"] == selected_edit_id
        ].iloc[0]

        current_class_type = (
            selected_row["class_type"]
            if selected_row["class_type"] in CLASS_TYPES
            else CLASS_TYPES[0]
        )

        current_level = (
            selected_row["level"]
            if selected_row["level"] in LEVELS
            else LEVELS[0]
        )

        with st.form(
            "edit_ballet_class_form"
        ):
            edit_date = st.date_input(
                "Class Date",
                value=selected_row["class_date"].date(),
            )

            edit_start_time = st.time_input(
                "Start Time",
                value=pd.to_datetime(
                    str(selected_row["start_time"])
                ).time(),
            )

            edit_duration_hours = st.number_input(
                "Duration Hours",
                min_value=0.5,
                step=0.5,
                value=float(
                    selected_row["duration_hours"]
                ),
            )

            edit_city = st.text_input(
                "City",
                value=selected_row["city"] or "",
            )

            edit_studio = st.text_input(
                "Studio / Institution",
                value=selected_row["studio"] or "",
            )

            edit_address = st.text_input(
                "Address",
                value=selected_row["address"] or "",
            )

            edit_teacher = st.text_input(
                "Teacher",
                value=selected_row["teacher"] or "",
            )

            edit_class_type = st.selectbox(
                "Class Type",
                CLASS_TYPES,
                index=CLASS_TYPES.index(
                    current_class_type
                ),
            )

            edit_level = st.selectbox(
                "Level",
                LEVELS,
                index=LEVELS.index(
                    current_level
                ),
            )

            edit_notes = st.text_area(
                "Notes",
                value=selected_row["notes"] or "",
            )

            submitted_edit = st.form_submit_button(
                "Save Changes",
                use_container_width=True,
            )

            if submitted_edit:
                update_ballet_class(
                    selected_edit_id,
                    {
                        "class_date": str(edit_date),
                        "start_time": str(edit_start_time),
                        "duration_hours": float(
                            edit_duration_hours
                        ),
                        "city": edit_city.strip(),
                        "studio": edit_studio.strip(),
                        "address": edit_address.strip(),
                        "teacher": edit_teacher.strip(),
                        "class_type": edit_class_type,
                        "level": edit_level,
                        "notes": edit_notes.strip(),
                    },
                )

                st.success(
                    "Class updated."
                )
                st.rerun()

    st.divider()
    st.subheader("Status")

    status_tables = get_ballet_status_tables(
        filtered_df
    )

    col8, col9 = st.columns(2)
    with col8:
        st.write(
            "Hours by City"
        )
        st.dataframe(
            status_tables["city_hours"],
            use_container_width=True,
            hide_index=True,
        )
    with col9:
        st.write(
            "Hours by Teacher"
        )
        st.dataframe(
            status_tables["teacher_hours"],
            use_container_width=True,
            hide_index=True,
        )