import streamlit as st

from utils.time_utils import today_bj_date
from services.fermentation_service import (
    add_pickle_batch,
    get_pickle_rows,
    get_pickle_summary,
    update_pickle_status,
    delete_pickle_batch,
)


def render_pickles():
    st.subheader("Pickles 🥬")

    with st.form(
        "add_pickle_form",
        clear_on_submit=True,
    ):
        batch_name = st.text_input(
            "Batch Name"
        )

        start_date = st.date_input(
            "Start Date",
            value=today_bj_date(),
        )

        ingredient = st.text_input(
            "Main Ingredient",
            placeholder="Cabbage / Radish / Cucumber",
        )

        ingredient_weight_g = st.number_input(
            "Ingredient Weight (g)",
            min_value=0.0,
            step=10.0,
        )

        col1, col2 = st.columns(2)
        with col1:
            salt_g = st.number_input(
                "Salt (g)",
                min_value=0.0,
                step=1.0,
            )
        with col2:
            water_ml = st.number_input(
                "Water (ml)",
                min_value=0.0,
                step=10.0,
            )

        method = st.selectbox(
            "Method",
            [
                "Brine",
                "Dry Salt",
                "Other",
            ],
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
                add_pickle_batch(
                    batch_name=batch_name.strip(),
                    start_date=str(start_date),
                    ingredient=ingredient.strip(),
                    ingredient_weight_g=float(
                        ingredient_weight_g
                    ),
                    salt_g=float(salt_g),
                    water_ml=float(water_ml),
                    method=method,
                    notes=notes.strip(),
                )

                st.success(
                    "Pickle batch added."
                )

                st.rerun()

    st.divider()

    rows = get_pickle_rows()
    summary = get_pickle_summary(rows)

    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Active Batches",
            summary["active_count"],
        )
    with col2:
        oldest_batch = summary["oldest_batch"]

        if oldest_batch:
            st.metric(
                "Oldest Active",
                f"{oldest_batch['fermentation_days']} days",
            )
            st.caption(
                oldest_batch["batch_name"]
            )
        else:
            st.metric(
                "Oldest Active",
                "-"
            )

    st.divider()

    if not rows:
        st.info(
            "No pickle batches yet."
        )
        return

    for row in rows:
        st.markdown(
            f"### {row['batch_name']}"
        )

        details = []

        if row.get("ingredient"):
            details.append(
                row["ingredient"]
            )

        if row.get("method"):
            details.append(
                row["method"]
            )

        details.append(
            f"{row['fermentation_days']} days"
        )

        if details:
            st.caption(
                " · ".join(details)
            )

        col1, col2, col3 = st.columns(3)
        with col1:
            if row.get("ingredient_weight_g"):
                st.caption(
                    f"Ingredient: "
                    f"{row['ingredient_weight_g']:g} g"
                )
        with col2:
            if row.get("salt_g"):
                st.caption(
                    f"Salt: {row['salt_g']:g} g"
                )
        with col3:
            if row.get("water_ml"):
                st.caption(
                    f"Water: {row['water_ml']:g} ml"
                )

        if row.get("salt_percentage") is not None:
            salt_basis = row.get(
                "salt_percentage_basis"
            )
            if salt_basis == "Water":
                salt_label = "Brine concentration"
            elif salt_basis == "Ingredient":
                salt_label = "Salt / ingredient weight"
            else:
                salt_label = "Salt percentage"

            st.caption(
                f"{salt_label}: "
                f"{row['salt_percentage']:.2f}%"
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
            key=f"pickle_status_{row['id']}",
        )

        col4, col5 = st.columns(2)
        with col4:
            if st.button(
                "Update Status",
                key=f"update_pickle_{row['id']}",
                use_container_width=True,
            ):
                update_pickle_status(
                    row["id"],
                    new_status,
                )

                st.success(
                    "Status updated."
                )
                st.rerun()
        with col5:
            if st.button(
                "Delete",
                key=f"delete_pickle_{row['id']}",
                use_container_width=True,
            ):
                delete_pickle_batch(
                    row["id"]
                )

                st.success(
                    "Batch deleted."
                )
                st.rerun()

        st.divider()