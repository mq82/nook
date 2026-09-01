import streamlit as st

from services.home_service import (
    add_shopping_item,
    get_shopping_items,
    mark_shopping_item_purchased,
    undo_shopping_item,
    delete_shopping_item,
)


def render_shopping():

    st.subheader("Shopping List 🛒")

    with st.form("shopping_form", clear_on_submit=True):

        name = st.text_input("Item Name")

        category = st.selectbox(
            "Category",
            [
                "Vegetable",
                "Fruit",
                "Meat",
                "Seafood",
                "Dairy",
                "Drink",
                "Snack",
                "Household",
                "Other",
            ],
        )

        col1, col2 = st.columns(2)

        with col1:
            quantity = st.number_input(
                "Quantity",
                min_value=0.0,
                step=1.0,
            )

        with col2:
            unit = st.text_input(
                "Unit",
                placeholder="pcs / g / ml",
            )

        notes = st.text_area("Notes")

        submitted = st.form_submit_button(
            "Add Item",
            use_container_width=True,
        )

        if submitted:

            if not name.strip():
                st.warning("Please enter item name.")

            else:

                add_shopping_item(
                    name.strip(),
                    category,
                    float(quantity),
                    unit.strip(),
                    notes.strip(),
                )

                st.success("Shopping item added.")

                st.rerun()

    st.divider()

    shopping = get_shopping_items()
    pending_items = shopping["pending"]
    purchased_items = shopping["purchased"]

    st.markdown("## 🛒 To Buy")

    if not pending_items:

        st.caption("Nothing to buy.")

    else:

        for item in pending_items:

            col1, col2 = st.columns([8, 1])

            with col1:

                st.markdown(
                    f"### {item['name']}"
                )

                details = []

                if item.get("category"):
                    details.append(item["category"])

                if item.get("quantity"):

                    qty = f"{item['quantity']:g}"

                    if item.get("unit"):
                        qty += f" {item['unit']}"

                    details.append(qty)

                if details:
                    st.caption(
                        " · ".join(details)
                    )

                notes = (item.get("notes") or "").strip()

                if notes:
                    st.caption(f"📝 {notes}")

            with col2:

                if st.button(
                    "✅",
                    key=f"buy_{item['id']}",
                    use_container_width=True,
                ):

                    mark_shopping_item_purchased(
                        item["id"]
                    )

                    st.rerun()

            st.divider()

    with st.expander(
        f"Purchased ({len(purchased_items)})"
    ):

        if not purchased_items:

            st.caption("No purchased items.")

        else:

            for item in purchased_items:

                col1, col2 = st.columns([8, 1])

                with col1:

                    st.markdown(
                        f"~~{item['name']}~~"
                    )

                    if item.get("purchased_at"):
                        st.caption(
                            item["purchased_at"]
                        )

                with col2:

                    if st.button(
                        "↩️",
                        key=f"undo_{item['id']}",
                        use_container_width=True,
                    ):

                        undo_shopping_item(
                            item["id"]
                        )

                        st.rerun()

                st.divider()

    st.divider()

    if purchased_items:

        if st.button(
            "Delete Purchased Items",
            type="secondary",
            use_container_width=True,
        ):

            for item in purchased_items:
                delete_shopping_item(
                    item["id"]
                )

            st.success(
                "Purchased items deleted."
            )

            st.rerun()