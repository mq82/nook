import streamlit as st
from utils.home_db import (
    add_chore,
    get_all_chores,
    complete_chore,
    undo_chore,
    delete_chore,
)

def render_chores():
    st.subheader("Chores 🧹")

    current_user = st.selectbox("Current User", ["Vera", "Ping Ping"])

    with st.form("add_chore_form", clear_on_submit=True):
        new_title = st.text_input("What needs to be done?")
        submitted = st.form_submit_button("Add Chore", use_container_width=True)

        if submitted:
            if new_title.strip():
                add_chore(new_title.strip())
                st.success("Chore added.")
                st.rerun()
            else:
                st.warning("Please enter a chore title.")

    st.divider()

    chores = get_all_chores()

    todo_chores = [chore for chore in chores if not chore["completed"]]
    done_chores = [chore for chore in chores if chore["completed"]]

    todo_chores.sort(
        key=lambda x: x["created_at"]
    )

    done_chores.sort(
        key=lambda x: x["completed_at"],
        reverse=True,
    )

    st.subheader("To Do")

    if not todo_chores:
        st.caption("Nothing here. Nice.")
    else:
        for chore in todo_chores:
            col1, col2 = st.columns([6, 1.5])

            with col1:
                with st.container(border=True):
                    st.markdown(f"### ☐ {chore['title']}")
                    st.caption(f"Created {chore['created_at']}")

            with col2:
                if st.button(
                    "✅",
                    key=f"complete_{chore['id']}",
                    use_container_width=True,
                ):
                    complete_chore(chore["id"], current_user)
                    st.rerun()

                if st.button(
                    "🗑",
                    key=f"delete_todo_{chore['id']}",
                    use_container_width=True,
                ):
                    delete_chore(chore["id"])
                    st.success("Chore deleted.")
                    st.rerun()

            st.divider()

    with st.expander(f"Completed ({len(done_chores)})", expanded=False):
        if not done_chores:
            st.caption("No completed chores yet.")
        else:
            for chore in done_chores:
                col1, col2 = st.columns([8, 1])

                with col1:
                    with st.container(border=True):
                        st.markdown(f"### ✅ ~~{chore['title']}~~")
                        st.caption(
                            f"Done by {chore['completed_by']} · {chore['completed_at']}"
                        )

                with col2:
                    if st.button("↩️", key=f"undo_{chore['id']}", use_container_width=True):
                        undo_chore(chore["id"])
                        st.rerun()

                    if st.button("🗑", key=f"delete_done_{chore['id']}", use_container_width=True):
                        delete_chore(chore["id"])
                        st.success("Chore deleted.")
                        st.rerun()

                st.divider()
