import streamlit as st
import pandas as pd
from datetime import date

from utils.home_db import (
    add_inventory_item,
    get_inventory_items,
    delete_inventory_item,
)


def render_fridge_inventory():
    st.subheader("Fridge Inventory 🧊")

    with st.form("add_inventory_form", clear_on_submit=True):
        name = st.text_input("Item Name")

        category = st.selectbox(
            "Category",
            ["Vegetable", "Fruit", "Meat", "Seafood", "Dairy", "Drink", "Sauce", "Other"]
        )

        location = st.selectbox(
            "Location",
            ["Fridge", "Freezer", "Pantry", "Other"]
        )

        col1, col2 = st.columns(2)
        with col1:
            quantity = st.number_input("Quantity", min_value=0.0, step=1.0)
        with col2:
            unit = st.text_input("Unit", placeholder="g / ml / pcs / box")

        col3, col4 = st.columns(2)
        with col3:
            purchase_date = st.date_input("Purchase Date", value=date.today())
        with col4:
            expiry_date = st.date_input("Expiry Date", value=date.today())

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Item", use_container_width=True)

        if submitted:
            if name.strip():
                add_inventory_item(
                    name.strip(),
                    category,
                    location,
                    float(quantity),
                    unit.strip(),
                    str(purchase_date),
                    str(expiry_date),
                    notes.strip()
                )
                st.success("Inventory item added.")
                st.rerun()
            else:
                st.warning("Please enter item name.")

    st.divider()

    items = get_inventory_items()

    if not items:
        st.info("No inventory items yet.")
        return

    df = pd.DataFrame(items)

    if "expiry_date" in df.columns:
        df["expiry_date"] = pd.to_datetime(df["expiry_date"])
        df["days_until_expiry"] = (df["expiry_date"].dt.date - date.today()).apply(lambda x: x.days)

    st.subheader("Current Inventory")

    location_options = ["All"] + sorted(df["location"].dropna().unique().tolist())
    category_options = ["All"] + sorted(df["category"].dropna().unique().tolist())

    col5, col6 = st.columns(2)

    with col5:
        location_filter = st.selectbox("Filter by Location", location_options)

    with col6:
        category_filter = st.selectbox("Filter by Category", category_options)

    filtered_df = df.copy()

    if location_filter != "All":
        filtered_df = filtered_df[filtered_df["location"] == location_filter]

    if category_filter != "All":
        filtered_df = filtered_df[filtered_df["category"] == category_filter]

    display_columns = [
        "name",
        "category",
        "location",
        "quantity",
        "unit",
        "purchase_date",
        "expiry_date",
        "days_until_expiry",
        "notes",
    ]

    existing_columns = [col for col in display_columns if col in filtered_df.columns]

    st.dataframe(
        filtered_df[existing_columns],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("Remove Item")

    item_options = {
        f'{row["name"]} | {row["location"]} | expires {row.get("expiry_date", "")}': row["id"]
        for _, row in filtered_df.iterrows()
    }

    if item_options:
        selected_item = st.selectbox(
            "Choose item to remove",
            list(item_options.keys())
        )

        if st.button("Remove Selected Item", use_container_width=True):
            delete_inventory_item(item_options[selected_item])
            st.success("Item removed.")
            st.rerun()