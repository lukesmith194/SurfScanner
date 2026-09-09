import streamlit as st

import auth
import nav_pages
import social
from avatars import resize_avatar
from boards import BOARD_TYPES
from header import render_user_indicator
from remember import clear_remember_cookie
from spots import DEPARTURE_CITIES

SURF_LEVELS = ["Beginner", "Intermediate", "Advanced"]


def _go_home():
    # Pages defined from callables (as main.py's are) are only targetable by
    # st.switch_page via their actual Page object, not a string path — see
    # nav_pages.py, which main.py populates for exactly this purpose.
    st.switch_page(nav_pages.home_page)


def _login_form():
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        remember_me = st.checkbox("Remember me", value=True)
        submitted = st.form_submit_button("Log in", icon=":material/login:", type="primary")
    if submitted:
        result = auth.log_in(email, password)
        if result.ok:
            st.session_state["user_id"] = result.user_id
            if remember_me:
                # Deferred to the destination page — see
                # remember.apply_pending_remember_cookie for why setting it
                # here, before switching pages, isn't safe.
                st.session_state["_pending_remember_user_id"] = result.user_id
            _go_home()
        else:
            st.error(result.error)


def _signup_form():
    with st.form("signup_form"):
        display_name = st.text_input("Display name")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password", help="At least 8 characters.")
        home_city = st.selectbox("Where do you usually travel from?", list(DEPARTURE_CITIES.keys()))
        surf_level = st.selectbox("Your surfing level", SURF_LEVELS, index=1)
        submitted = st.form_submit_button("Create account", icon=":material/person_add:", type="primary")
    if submitted:
        result = auth.sign_up(email, password, display_name, home_city, surf_level)
        if result.ok:
            st.session_state["user_id"] = result.user_id
            st.session_state["_pending_remember_user_id"] = result.user_id
            _go_home()
        else:
            st.error(result.error)


def _logged_out_view():
    st.write(
        "Create an account to post planned trips and follow other surfers "
        "on the Community page."
    )
    _, center, _ = st.columns([1, 2, 1])
    with center:
        with st.container(border=True):
            login_tab, signup_tab = st.tabs(
                [
                    ":material/login: Log in",
                    ":material/person_add: Sign up",
                ]
            )
            with login_tab:
                _login_form()
            with signup_tab:
                _signup_form()


def _avatar(user):
    if user.avatar:
        st.image(user.avatar, width=100)
    else:
        with st.container(border=True, width=100, height=100, horizontal_alignment="center"):
            st.markdown("# :material/account_circle:")


def _profile_header(user_id: int, user):
    col1, col2 = st.columns([1, 4], vertical_alignment="center")
    with col1:
        _avatar(user)
    with col2:
        st.write(f"### {user.display_name}")
        st.caption(user.email)
        with st.container(horizontal=True):
            st.badge(user.home_city, icon=":material/location_on:")
            st.badge(user.surf_level, icon=":material/waves:")
            if user.board_type:
                st.badge(user.board_type, icon=":material/surfing:")

    uploaded = st.file_uploader(
        "Update profile picture", type=["png", "jpg", "jpeg"], key="avatar_upload"
    )
    if uploaded is not None:
        social.update_avatar(user_id, resize_avatar(uploaded.getvalue()))
        st.rerun()


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
        board_index = BOARD_TYPES.index(user.board_type) if user.board_type in BOARD_TYPES else 0
        board_type = st.selectbox("Preferred board type", BOARD_TYPES, index=board_index)
        saved = st.form_submit_button("Save changes", icon=":material/check_circle:", type="primary")
    if saved:
        social.update_profile(user_id, display_name, home_city, surf_level, board_type)
        st.success("Profile updated.")
        st.rerun()

    if st.button("Log out", icon=":material/logout:"):
        clear_remember_cookie()
        del st.session_state["user_id"]
        st.rerun()


def _password_tab(user_id: int):
    with st.form("change_password_form", clear_on_submit=True):
        current_password = st.text_input("Current password", type="password")
        new_password = st.text_input("New password", type="password", help="At least 8 characters.")
        confirm_password = st.text_input("Confirm new password", type="password")
        submitted = st.form_submit_button("Change password", icon=":material/key:", type="primary")

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
        st.caption("No trips posted yet — plan one on the Trip planner page or post one on Community.")
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
    _profile_header(user_id, user)

    profile_tab, password_tab, trips_tab = st.tabs(
        [
            ":material/edit: Profile",
            ":material/lock: Change password",
            ":material/luggage: My trips",
        ]
    )
    with profile_tab:
        _profile_tab(user_id, user)
    with password_tab:
        _password_tab(user_id)
    with trips_tab:
        _trips_tab(user_id)


def app():
    render_user_indicator()
    st.title("Account", icon=":material/account_circle:")

    user_id = st.session_state.get("user_id")
    if user_id:
        _profile_view(user_id)
        return

    _logged_out_view()
