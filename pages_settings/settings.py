import streamlit as st
import pandas as pd
from utils.master_data import get_options, add_option, update_option_status, delete_option


OPTION_GROUPS = {
    "Supplements": "supplements",
    "Meal Types": "meal_types",
    "Inventory Categories": "inventory_categories",
    "Inventory Locations": "inventory_locations",
    "Ballet Class Types": "ballet_class_types",
    "Ballet Levels": "ballet_levels",
    "Ballet Teachers": "ballet_teachers",
    "Ballet Studios": "ballet_studios",
}


def render_settings():
    st.subheader("Settings ⚙️")

    group_label = st.selectbox("Data Dictionary", list(OPTION_GROUPS.keys()))
    option_group = OPTION_GROUPS[group_label]

    with st.form("add_option_form", clear_on_submit=True):
        label = st.text_input("New Option")
        sort_order = st.number_input("Sort Order", min_value=0, step=10, value=0)
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Option", use_container_width=True)

        if submitted:
            if label.strip():
                add_option(option_group, label.strip(), sort_order, notes)
                st.success("Option added.")
                st.rerun()
            else:
                st.warning("Please enter an option.")

    st.divider()

    options = get_options(option_group, include_inactive=True)

    if not options:
        st.info("No options yet.")
        return

    df = pd.DataFrame(options)
    st.dataframe(
        df[["label", "value", "sort_order", "is_active", "notes"]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("Update Option Status")

    option_map = {
        f'{row["label"]} | active={row["is_active"]}': row["id"]
        for _, row in df.iterrows()
    }

    selected = st.selectbox("Choose option", list(option_map.keys()))

    new_status = st.selectbox(
        "New Status",
        [True, False],
        format_func=lambda x: "Active" if x else "Inactive",
        key="settings_new_status",
    )

    if st.button(
        "Update Status",
        key="settings_update_status",
        use_container_width=True,
        ):
        update_option_status(option_map[selected], new_status)
        st.success("Status updated.")
        st.rerun()

    if st.button(
        "Delete Option",
        key="settings_delete_option",
        use_container_width=True,
        ):
        delete_option(option_map[selected])
        st.success("Option deleted.")
        st.rerun()