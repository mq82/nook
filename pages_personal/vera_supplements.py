import streamlit as st

from utils.supplement_db import (
    get_active_supplements,
    get_active_bottles_by_supplement,
    calculate_bottle_remaining,
    add_legacy_supplement_log,
    add_supplement_intake,
    delete_supplement_intake,
    get_supplement_intakes_by_date,
    get_supplement_intake_daily_summary,
)

from services.supplement_service import(
    enrich_bottle_with_remaining,
    build_bottle_label,
)

def render_vera_supplements():
    st.subheader("Vera Supplements Log")

    st.caption("Record what you take at the current time. No manual date/time input.")

    active_supplements = get_active_supplements()

    if not active_supplements:
        st.warning("Please add supplements in Supplement Library first.")
        return

    all_bottle_options = {}

    for supplement in active_supplements:
        active_bottles = get_active_bottles_by_supplement(
            supplement["id"]
        )

    for bottle in active_bottles:
        bottle = enrich_bottle_with_remaining(bottle)

        label = build_bottle_label(
            supplement,
            bottle
        )

        all_bottle_options[label] = {
            "supplement": supplement,
            "bottle": bottle,
            "remaining": bottle["remaining"],
        }

    if not all_bottle_options:
        st.warning("No active supplement bottles found. Please add bottles in Supplement Library → Bottles.")
        return

    with st.form("add_supplement_form", clear_on_submit=True):
        selected_bottle_label = st.selectbox(
            "Bottle",
            list(all_bottle_options.keys())
        )

        selected = all_bottle_options[selected_bottle_label]
        selected_supplement = selected["supplement"]
        selected_bottle = selected["bottle"]

        st.caption(f'Supplement: {selected_supplement["name"]}')
        st.caption(f'Remaining: {selected["remaining"]:g}')

        col1, col2 = st.columns(2)

        with col1:
            amount = st.number_input(
                "Amount",
                min_value=0.0,
                step=1.0
            )

        with col2:
            unit = st.text_input(
                "Unit",
                value=selected_bottle.get("unit")
                or selected_supplement.get("default_unit")
                or "capsule(s)"
            )

        note = st.text_area(
            "Note",
            placeholder="Optional: after lunch, felt dizzy, with food, etc."
        )

        submitted = st.form_submit_button("Add Log", use_container_width=True)

        if submitted:
            add_legacy_supplement_log(
                selected_supplement["name"],
                amount,
                unit,
                note.strip()
            )

            add_supplement_intake(
                person_name="vera",
                supplement_id=selected_supplement["id"],
                bottle_id=selected_bottle["id"],
                amount=amount,
                unit=unit,
                notes=note.strip()
            )

            st.success("Supplement log added.")
            st.rerun()

    st.divider()

    selected_supplement_date = st.date_input("Select Date")
    selected_date_str = str(selected_supplement_date)

    st.markdown(f"### Daily Summary - {selected_date_str}")

    summary = get_supplement_intake_daily_summary(selected_date_str)

    if not summary:
        st.caption("No supplements recorded on this date.")
    else:
        for item in summary:
            st.markdown(
                f"- **{item['supplement_name']}**: "
                f"{item['total_amount']} {item['unit']}"
            )

    st.divider()

    st.markdown(f"### Logs - {selected_date_str}")

    intakes = get_supplement_intakes_by_date(selected_date_str)

    supplement_filter_options = ["All"] + sorted(
        list(set(item["supplement_name"] for item in intakes))
    ) if intakes else ["All"]

    selected_filter = st.selectbox(
        "Filter by Supplement",
        supplement_filter_options
    )

    if selected_filter != "All":
        intakes = [
            item for item in intakes
            if item["supplement_name"] == selected_filter
        ]

    if not intakes:
        st.caption("No supplement intakes for this date.")
    else:
        for intake in intakes:
            col1, col2 = st.columns([6, 1.5])

            with col1:
                st.markdown(
                    f"### {intake['supplement_name']} - "
                    f"{intake['amount']} {intake['unit']}"
                )

                if intake["bottle_label"]:
                    st.caption(f"Bottle: {intake['bottle_label']}")

                st.caption(f"Taken at: {intake['taken_at']}")

                if intake["notes"]:
                    st.caption(f"Note: {intake['notes']}")

            with col2:
                if st.button(
                    "Delete",
                    key=f"delete_intake_{intake['id']}",
                    use_container_width=True
                ):
                    delete_supplement_intake(intake["id"])
                    st.success("Supplement intake deleted.")
                    st.rerun()

            st.divider()