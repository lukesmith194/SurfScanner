import streamlit as st

import auth
import social
from spots import DEPARTURE_CITIES

SURF_LEVELS = ["Beginner", "Intermediate", "Advanced"]


def _login_form():
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in")
    if submitted:
        result = auth.log_in(email, password)
        if result.ok:
            st.session_state["user_id"] = result.user_id
            st.rerun()
        else:
            st.error(result.error)


def _signup_form():
    with st.form("signup_form"):
        display_name = st.text_input("Display name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password", help="At least 8 characters.")
        home_city = st.selectbox("Where do you usually travel from?", list(DEPARTURE_CITIES.keys()))
        surf_level = st.selectbox("Your surfing level", SURF_LEVELS, index=1)
        submitted = st.form_submit_button("Create account")
    if submitted:
        result = auth.sign_up(email, password, display_name, home_city, surf_level)
        if result.ok:
            st.session_state["user_id"] = result.user_id
            st.rerun()
        else:
            st.error(result.error)


def _profile_tab(user_id: int, user):
    with st.form("edit_profile_form"):
        display_name = st.text_input("Display name", value=user.display_name)
        home_city = st.selectbox(
            "Where do you usually travel from?",
            list(DEPARTURE_CITIES.keys()),
            index=list(DEPARTURE_CITIES.keys()).index(user.home_city),
        )
        surf_level = st.selectbox(
            "Your surfing level", SURF_LEVELS, index=SURF_LEVELS.index(user.surf_level)
        )
        saved = st.form_submit_button("Save changes")
    if saved:
        social.update_profile(user_id, display_name, home_city, surf_level)
        st.success("Profile updated.")
        st.rerun()

    if st.button("Log out"):
        del st.session_state["user_id"]
        st.rerun()


def _password_tab(user_id: int):
    with st.form("change_password_form", clear_on_submit=True):
        current_password = st.text_input("Current password", type="password")
        new_password = st.text_input("New password", type="password", help="At least 8 characters.")
        confirm_password = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Change password")

    if not submitted:
        return
    if new_password != confirm_password:
        st.error("New password and confirmation don't match.")
        return
    result = auth.change_password(user_id, current_password, new_password)
    if result.ok:
        st.success("Password changed.")
    else:
        st.error(result.error)


def _trips_tab(user_id: int):
    posts = social.posts_by_user(user_id)
    if not posts:
        st.caption("No trips posted yet — plan one on the Trip Planner page or post one on Community.")
        return
    for post in posts:
        with st.container(border=True):
            st.write(
                f"**{post.spot_name}** · {post.start_date:%b %d} – {post.end_date:%b %d} · {post.level}"
            )
            if post.note:
                st.caption(post.note)
            st.caption(f"{post.interest_count} interested · {post.comment_count} comment(s)")


def _profile_view(user_id: int):
    user = social.get_user(user_id)
    st.write(f"### {user.display_name}")
    st.caption(user.email)

    profile_tab, password_tab, trips_tab = st.tabs(["Profile", "Change password", "My trips"])
    with profile_tab:
        _profile_tab(user_id, user)
    with password_tab:
        _password_tab(user_id)
    with trips_tab:
        _trips_tab(user_id)


def app():
    st.write("## Account")

    user_id = st.session_state.get("user_id")
    if user_id:
        _profile_view(user_id)
        return

    st.write(
        "Create an account to post planned trips and follow other surfers "
        "on the Community page."
    )
    login_tab, signup_tab = st.tabs(["Log in", "Sign up"])
    with login_tab:
        _login_form()
    with signup_tab:
        _signup_form()
