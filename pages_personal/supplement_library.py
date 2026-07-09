import streamlit as st
import pandas as pd
from utils.supabase_client import get_supabase_client
from utils.supplement_db import calculate_bottle_remaining


def render_supplement_library():
    st.subheader("Supplement Library")

    supabase = get_supabase_client()

    page = st.segmented_control(
        "Choose Section",
        ["Supplements", "Bottles"],
        default="Supplements"
    )

    if page == "Supplements":
        render_supplements_section(supabase)

    elif page == "Bottles":
        render_bottles_section(supabase)


def render_supplements_section(supabase):
    st.markdown("### Supplements")

    with st.form("add_supplement_entity_form", clear_on_submit=True):
        name = st.text_input("Supplement Name")
        category = st.text_input("Category", placeholder="e.g. mineral, vitamin, amino acid")
        default_unit = st.text_input("Default Unit", placeholder="e.g. mg, IU, capsule(s)")
        description = st.text_area("Description")
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Supplement", use_container_width=True)

        if submitted:
            if name.strip():
                supabase.table("supplements").insert({
                    "name": name.strip(),
                    "category": category.strip() or None,
                    "default_unit": default_unit.strip() or None,
                    "description": description.strip() or None,
                    "notes": notes.strip() or None,
                    "is_active": True,
                }).execute()

                st.success("Supplement added.")
                st.rerun()
            else:
                st.warning("Please enter supplement name.")

    st.divider()

    result = (
        supabase
        .table("supplements")
        .select("*")
        .order("name", desc=False)
        .execute()
    )

    records = result.data

    if not records:
        st.info("No supplements yet.")
        return

    df = pd.DataFrame(records)

    st.dataframe(
        df[["name", "category", "default_unit", "is_active", "notes"]],
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("Update Supplement Status")

    supplement_options = {
        f'{row["name"]} | active={row["is_active"]}': row["id"]
        for _, row in df.iterrows()
    }

    selected = st.selectbox(
        "Choose supplement",
        list(supplement_options.keys()),
        key="supplement_library_status_select"
    )

    new_status = st.selectbox(
        "New Status",
        [True, False],
        format_func=lambda x: "Active" if x else "Inactive",
        key="supplement_library_status_value"
    )

    if st.button(
        "Update Supplement Status",
        key="supplement_library_update_status",
        use_container_width=True
    ):
        supabase.table("supplements").update({
            "is_active": new_status
        }).eq("id", supplement_options[selected]).execute()

        st.success("Supplement status updated.")
        st.rerun()


def render_bottles_section(supabase):
    st.markdown("### Supplement Bottles")

    supplements_result = (
        supabase
        .table("supplements")
        .select("*")
        .eq("is_active", True)
        .order("name", desc=False)
        .execute()
    )

    supplements = supplements_result.data

    if not supplements:
        st.warning("Please add supplements first.")
        return

    supplement_map = {
        item["name"]: item["id"]
        for item in supplements
    }

    with st.form("add_supplement_bottle_form", clear_on_submit=True):
        supplement_name = st.selectbox(
            "Supplement",
            list(supplement_map.keys())
        )

        brand = st.text_input("Brand", placeholder="e.g. NOW, California Gold, Life Extension")
        product_name = st.text_input("Product Name")
        strength = st.text_input("Strength", placeholder="e.g. 200mg per capsule")
        unit = st.text_input("Unit", placeholder="e.g. capsule(s), tablet(s), ml")

        quantity = st.number_input(
            "Quantity",
            min_value=0.0,
            step=1.0
        )

        col1, col2 = st.columns(2)

        with col1:
            purchase_date = st.date_input("Purchase Date", value=None)

        with col2:
            expiry_date = st.date_input("Expiry Date", value=None)

        col3, col4 = st.columns(2)

        with col3:
            opened_date = st.date_input("Opened Date", value=None)

        with col4:
            finished_date = st.date_input("Finished Date", value=None)

        purchase_place = st.text_input("Purchase Place", placeholder="e.g. iHerb, JD, Taobao")
        price = st.number_input("Price", min_value=0.0, step=1.0)
        lot_number = st.text_input("Lot Number")

        status = st.selectbox(
            "Status",
            ["active", "finished", "discarded"]
        )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Bottle", use_container_width=True)

        if submitted:
            supabase.table("supplement_bottles").insert({
                "supplement_id": supplement_map[supplement_name],
                "brand": brand.strip() or None,
                "product_name": product_name.strip() or None,
                "strength": strength.strip() or None,
                "unit": unit.strip() or None,
                "quantity": float(quantity),
                "purchase_date": str(purchase_date) if purchase_date else None,
                "expiry_date": str(expiry_date) if expiry_date else None,
                "opened_date": str(opened_date) if opened_date else None,
                "finished_date": str(finished_date) if finished_date else None,
                "purchase_place": purchase_place.strip() or None,
                "price": float(price) if price else None,
                "lot_number": lot_number.strip() or None,
                "status": status,
                "notes": notes.strip() or None,
            }).execute()

            st.success("Bottle added.")
            st.rerun()

    st.divider()

    bottles_result = (
        supabase
        .table("supplement_bottles")
        .select("*, supplements(name)")
        .order("created_at", desc=True)
        .execute()
    )

    bottles = bottles_result.data

    if not bottles:
        st.info("No supplement bottles yet.")
        return

    rows = []

    for bottle in bottles:
        supplement = bottle.get("supplements") or {}

        remaining = calculate_bottle_remaining(
            bottle["id"],
            bottle.get("initial_quantity") or bottle.get("quantity")
        )

        rows.append({
            "id": bottle["id"],
            "supplement": supplement.get("name"),
            "brand": bottle.get("brand"),
            "product_name": bottle.get("product_name"),
            "strength": bottle.get("strength"),
            "initial_quantity": bottle.get("initial_quantity") or bottle.get("quantity"),
            "remaining": remaining,
            "unit": bottle.get("unit"),
            "purchase_date": bottle.get("purchase_date"),
            "expiry_date": bottle.get("expiry_date"),
            "opened_date": bottle.get("opened_date"),
            "finished_date": bottle.get("finished_date"),
            "status": bottle.get("status"),
            "notes": bottle.get("notes"),
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df.drop(columns=["id"]),
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("Low Stock Bottles")

    low_stock_df = df[
        (df["status"] == "active") &
        (df["remaining"] <= 10)
    ]

    if low_stock_df.empty:
        st.caption("No low stock bottles.")
    else:
        for _, row in low_stock_df.iterrows():
            st.warning(
                f'{row["supplement"]} | '
                f'{row["brand"] or ""} | '
                f'{row["remaining"]:g} {row["unit"] or ""} left'
            )

    st.divider()
    st.subheader("Update Bottle Status")

    bottle_options = {
        f'{row["supplement"]} | {row["brand"] or ""} | {row["product_name"] or ""} | {row["status"]}': row["id"]
        for _, row in df.iterrows()
    }

    selected_bottle = st.selectbox(
        "Choose bottle",
        list(bottle_options.keys()),
        key="bottle_status_select"
    )

    new_status = st.selectbox(
        "New Status",
        ["active", "finished", "discarded"],
        key="bottle_new_status"
    )

    if st.button(
        "Update Bottle Status",
        key="update_bottle_status",
        use_container_width=True
    ):
        update_data = {
            "status": new_status
        }

        if new_status == "finished":
            from datetime import date
            update_data["finished_date"] = str(date.today())

        supabase.table("supplement_bottles").update(
            update_data
        ).eq("id", bottle_options[selected_bottle]).execute()

        st.success("Bottle status updated.")
        st.rerun()