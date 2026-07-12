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
        location_filter = st.selectbox(
            "Location",
            location_options
       )

    with col6:
        category_filter = st.selectbox(
            "Category",
            category_options
        )

    filtered_df = df.copy()

    if location_filter != "All":
        filtered_df = filtered_df[
            filtered_df["location"] == location_filter
        ]

    if category_filter != "All":
        filtered_df = filtered_df[
            filtered_df["category"] == category_filter
        ]

    filtered_df = filtered_df.sort_values(
        "expiry_date",
        ascending=True,
        na_position="last"
    )

    st.divider()
    
    for _, item in filtered_df.iterrows():
        col1, col2 = st.columns([8,1])
        
        with col1:
            st.markdown(f"### {item['name']}")
            info = f"{item['quantity']:g} {item['unit']}"

            if item["location"]:
                info += f" · 📍 {item['location']}"

            st.caption(info)

            if pd.notna(item["expiry_date"]):
                days = int(item["days_until_expiry"])

                if days < 0:
                    st.error(f"Expired {-days} day(s) ago")

                elif days == 0:
                    st.warning("Expires today")
    
                elif days == 1:
                    st.warning("Expires tomorrow")

                else:
                    st.caption(f"Expires in {days} days")

            if item["notes"]:
                st.caption(item["notes"])

        with col2:

            if st.button(
                "🗑",
                key=f"delete_inventory_{item['id']}",
                use_container_width=True
            ):
                delete_inventory_item(item["id"])
                st.success("Item deleted.")
                st.rerun()

        st.divider()