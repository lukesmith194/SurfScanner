import extra_streamlit_components as stx
import streamlit as st

import auth
import nav_pages
from db import DATABASE_URL, init_db
from streamlit_pages import account, community, historical, home, predictions, spot_info, trip_planner

st.set_page_config(page_title="SurfScanner", page_icon="🏄")

init_db()

# One CookieManager instance per run, shared via session_state so account.py
# can set/delete the cookie on login/logout without instantiating a second
# component with the same key in the same run (Streamlit would reject that
# as a duplicate element).
cookie_manager = stx.CookieManager(key="cookie_manager")
st.session_state["_cookie_manager"] = cookie_manager

if "user_id" not in st.session_state:
    # "Remember me" — a real user who checked it on the login page gets a
    # long-lived opaque token in a browser cookie (auth.py verifies it
    # against its hash, never the raw value). Works both locally and once
    # deployed, since it's tied to a specific account, not a shared one.
    remember_token = cookie_manager.get("remember_token")
    remembered_user_id = auth.verify_remember_token(remember_token) if remember_token else None
    if remembered_user_id:
        st.session_state["user_id"] = remembered_user_id
    elif DATABASE_URL.startswith("sqlite"):
        # Dev convenience: auto-log-in as the seeded test account (see
        # seed_demo_data.py) on a fresh session, so Account/Community can be
        # checked without logging in by hand each time. Gated to local dev
        # only (no DATABASE_URL configured) — a real deployment always sets
        # DATABASE_URL (see db.py), so this never fires there. Without that
        # gate, every visitor to a public deployment would land
        # pre-logged-in as the same shared account.
        test_user_id = auth.get_user_id_by_email("test@surfscanner.com")
        if test_user_id:
            st.session_state["user_id"] = test_user_id

# Streamlit's top navigation renders small and left-packed by default. Blow
# it up to a full-width bar with bigger tabs — data-testid selectors are
# part of Streamlit's stable public contract, unlike the st-emotion-cache-*
# hashes next to them, which are regenerated per build and not safe to target.
st.markdown(
    """
    <style>
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        height: 4.5rem;
    }
    [data-testid="stToolbar"] .rc-overflow {
        width: 100%;
        justify-content: space-evenly;
    }
    [data-testid="stTopNavLinkContainer"] {
        flex: 1;
        display: flex;
        justify-content: center;
    }
    [data-testid="stTopNavLink"] {
        font-size: 1.2rem;
        padding: 0.9rem 1.5rem;
    }
    [data-testid="stTopNavLink"] [data-testid="stIconEmoji"] {
        font-size: 1.4rem;
    }
    /* Trip Planner and Community are the app's actual product — emphasize
       their nav tabs specifically. Streamlit renders each stTopNavLink as
       an <a> whose href is the page's url_path, so an attribute selector
       can target one tab without touching the generic stTopNavLink rule
       above (verified against the built frontend JS, which sets
       href={pageUrl} on this exact element). */
    [data-testid="stTopNavLink"][href*="trip-planner"],
    [data-testid="stTopNavLink"][href*="community"] {
        font-weight: 700;
        color: #ff4b4b;
        border-bottom: 3px solid #ff4b4b;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

home_page = st.Page(home.app, title="Home", icon="🏠", url_path="home", default=True)
account_page = st.Page(account.app, title="Account", icon="👤", url_path="account")
trip_planner_page = st.Page(trip_planner.app, title="Trip Planner", icon="🧳", url_path="trip-planner")
community_page = st.Page(community.app, title="Community", icon="👥", url_path="community")
pages = [
    home_page,
    # Trip Planner and Community are the app's actual product — placed
    # right after Home, ahead of the more reference-y pages below.
    trip_planner_page,
    community_page,
    st.Page(spot_info.app, title="Spot info", icon="🌊", url_path="spot-info"),
    st.Page(historical.app, title="Historical", icon="📊", url_path="historical"),
    st.Page(predictions.app, title="Predictions", icon="🔮", url_path="predictions"),
    account_page,
]

# Shared so streamlit_pages/*.py (via header.py) and account.py's post-login
# redirect can target these by their actual Page object — see nav_pages.py.
nav_pages.home_page = home_page
nav_pages.account_page = account_page
nav_pages.trip_planner_page = trip_planner_page
nav_pages.community_page = community_page

# st.navigation(...).run() must stay a single chained call — splitting it
# across two statements (e.g. `nav = st.navigation(...)` then `nav.run()`
# later, even with nothing else in between) was tried here to render a
# shared header before .run(), but it silently broke direct-URL routing to
# every non-default page. Each page renders its own header instead — see
# header.py and streamlit_pages/*.py.
st.navigation(pages, position="top").run()
