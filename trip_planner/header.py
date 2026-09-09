"""The persistent 'who's logged in' indicator shown at the top of every
page. Streamlit's own header (where "Deploy" and the ⋮ menu sit) isn't
something a page can inject content into, so each page renders this as the
first thing in its own content instead — the closest robust equivalent to a
top-right corner badge. Called from each streamlit_pages/*.py module rather
than once in main.py, simply to keep it right above that page's own title
regardless of which page is active.
"""

import streamlit as st

import nav_pages
import social
from remember import apply_pending_remember_cookie


def render_user_indicator() -> None:
    apply_pending_remember_cookie()

    _, indicator_col = st.columns([5, 1])
    with indicator_col:
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.page_link(nav_pages.account_page, label="Log in", icon="👤")
            return

        user = social.get_user(user_id)
        if not user.avatar:
            # No custom avatar: a single page_link, whose icon comes from
            # account_page's own icon="👤" — no need to render one ourselves
            # too (that was rendering a second, redundant icon).
            st.page_link(nav_pages.account_page, label=user.display_name)
            return

        # With a real avatar image, page_link can't display it directly (its
        # icon slot only takes an emoji/icon-font string), so show the photo
        # alongside the link — page_link still shows account_page's own
        # small icon next to the label here, since passing icon=None doesn't
        # suppress that inherited default and there's no documented "no
        # icon" value; a minor cosmetic overlap, not worth fighting further.
        avatar_col, name_col = st.columns([1, 4], vertical_alignment="center")
        with avatar_col:
            st.image(user.avatar, width=32)
        with name_col:
            st.page_link(nav_pages.account_page, label=user.display_name)
