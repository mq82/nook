import streamlit as st
from utils.home_db import add_meal, get_meals_by_date, delete_meal


def render_meals():
    st.subheader("Meals 🍽️")

    with st.form("add_meal_form", clear_on_submit=True):
        add_meal_date = st.date_input("Meal Date")

        meal_type = st.selectbox(
            "Meal Type",
            ["Breakfast", "Lunch", "Dinner", "Snack", "Other"]
        )

        meal_content = st.text_input("What did you eat?")

        submitted = st.form_submit_button("Add Meal", use_container_width=True)

        if submitted:
            if meal_content.strip():
                add_meal(str(add_meal_date), meal_type, meal_content.strip())
                st.session_state["meal_view_date"] = add_meal_date
                st.success("Meal added.")
                st.rerun()
            else:
                st.warning("Please enter meal content.")

    st.divider()

    st.subheader("View Meals by Date")

    view_meal_date = st.date_input(
        "View Date",
        key="meal_view_date"
    )

    meals = get_meals_by_date(str(view_meal_date))

    st.markdown(f"### Meals for {view_meal_date}")

    if not meals:
        st.caption("No meals recorded yet.")
        return

    for meal in meals:
        col1, col2 = st.columns([6, 1.5])

        with col1:
            st.markdown(f"**{meal['meal_type']}** - {meal['content']}")
            st.caption(f"Created at {meal['created_at']}")

        with col2:
            if st.button("Delete", key=f"delete_meal_{meal['id']}", use_container_width=True):
                delete_meal(meal["id"])
                st.success("Meal deleted.")
                st.rerun()

        st.divider()