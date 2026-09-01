import streamlit as st
import pandas as pd

from services.pingping_plan_service import (
    get_plan_form_data,
    add_plan,
    update_plan_status,
    get_plan_rows,
)


def render_pingping_plan():
    st.subheader("Pingping Supplement Plan")

    form_data = get_plan_form_data()
    if not form_data["supplement_names"]:
        st.warning(
            "Please add supplements in Supplement Library first."
        )
        return

    with st.form(
        "add_pingping_plan_form",
        clear_on_submit=True,
    ):
        supplement_name = st.selectbox(
            "Supplement",
            form_data["supplement_names"],
        )

        selected = form_data["supplement_options"][
            supplement_name
        ]

        selected_supplement = selected[
            "supplement"
        ]

        bottle_options = selected[
            "bottles"
        ]

        if bottle_options:
            selected_bottle_label = st.selectbox(
                "Bottle",
                list(bottle_options.keys()),
            )
            selected_bottle = bottle_options[
                selected_bottle_label
            ]
        else:
            selected_bottle = None

            st.caption(
                "No active bottle for this supplement. "
                "The plan can still be created without a bottle."
            )

        dosage = st.text_input(
            "Dosage",
            placeholder="e.g. 500mg, 1 capsule, etc.",
        )

        frequency = st.text_input(
            "Frequency",
            placeholder="e.g. Once daily, Twice daily, etc.",
        )

        timing = st.text_input(
            "Timing",
            placeholder="e.g. after breakfast, before bed, etc.",
        )

        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date"
            )
        with col2:
            end_date = st.date_input(
                "End Date"
            )

        notes = st.text_area("Notes")


        submitted = st.form_submit_button(
            "Add Supplement Plan",
            use_container_width=True,
        )
        if submitted:
            try:
                add_plan(
                    supplement_id=selected_supplement["id"],
                    bottle_id=(
                        selected_bottle["id"]
                        if selected_bottle
                        else None
                    ),
                    supplement_name=selected_supplement["name"],
                    dosage=dosage.strip() or None,
                    frequency=frequency.strip() or None,
                    timing=timing.strip() or None,
                    start_date=str(start_date),
                    end_date=(
                        str(end_date)
                        if end_date
                        else None
                    ),
                    notes=notes.strip() or None,
                )

                st.success(
                    "Supplement plan added successfully 💊"
                )
                st.rerun()

            except ValueError as e:
                st.error(str(e))

    st.divider()
    st.subheader("Current Supplement Plans")

    rows = get_plan_rows()

    if not rows:
        st.info("No supplement plans found.")
        return

    df = pd.DataFrame(rows)

    df["start_date"] = pd.to_datetime(
        df["start_date"]
    )

    df["end_date"] = pd.to_datetime(
        df["end_date"],
        errors="coerce",
    )

    show_active_only = st.checkbox(
        "Show Active Plans Only",
        value=True,
    )

    if show_active_only:
        df = df[
            df["is_active"] == True
        ]

    if df.empty:
        st.info("No active supplement plans found.")
        return

    display_columns = [
        "person",
        "supplement",
        "bottle",
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
        (
            f'{row["supplement"]} | '
            f'{row["bottle"] or ""} | '
            f'{row["timing"] or ""} | '
            f'active={row["is_active"]}'
        ): row["id"]
        for _, row in df.iterrows()
    }

    selected_plan = st.selectbox(
        "Choose plan",
        list(plan_options.keys()),
    )

    new_status = st.selectbox(
        "New Status",
        [True, False],
        format_func=lambda value: (
            "Active"
            if value
            else "Inactive"
        ),
    )

    if st.button(
        "Update Plan Status",
        use_container_width=True,
    ):
        update_plan_status(
            plan_options[selected_plan],
            new_status,
        )

        st.success("Plan status updated.")
        st.rerun()