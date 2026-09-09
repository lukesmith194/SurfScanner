"""Cookie-backed 'remember me' helpers — shared between account.py (which
sets/clears the cookie on login/logout) and header.py (which finishes a
*pending* cookie write after a post-login redirect; see
apply_pending_remember_cookie for why that's deferred rather than done
inline in the login handler).

Split out from account.py so both of those can import it without a circular
import (header.py is imported by every streamlit_pages/*.py module,
including account.py).
"""

import time
from datetime import datetime, timedelta

import streamlit as st

import auth


def set_remember_cookie(user_id: int) -> None:
    cookie_manager = st.session_state.get("_cookie_manager")
    if not cookie_manager:
        return
    token = auth.create_remember_token(user_id)
    cookie_manager.set(
        "remember_token",
        token,
        expires_at=datetime.utcnow() + timedelta(days=auth.REMEMBER_TOKEN_DAYS),
        key="set_remember_cookie",
    )
    # extra_streamlit_components writes the cookie via a round trip to the
    # browser. Confirmed by testing: an immediate st.rerun() or
    # st.switch_page() right after .set() can race against that round trip
    # and silently drop the cookie, or even silently drop the *navigation*
    # itself if the component's own rerun supersedes ours mid-sleep. This
    # delay gives the write a chance to land; see apply_pending_remember_
    # cookie() for how the navigation race is avoided entirely.
    time.sleep(0.5)


def clear_remember_cookie() -> None:
    cookie_manager = st.session_state.get("_cookie_manager")
    if not cookie_manager:
        return
    token = cookie_manager.get("remember_token")
    if token:
        # Revoke server-side first — this alone makes the cookie unusable
        # even if the browser-side delete below doesn't finish in time.
        auth.revoke_remember_token(token)
        cookie_manager.delete("remember_token", key="delete_remember_cookie")
        time.sleep(0.5)


def apply_pending_remember_cookie() -> None:
    """Call once per page render (see header.py, which every page calls).

    Login/signup used to set the cookie *before* st.switch_page() to the
    post-login destination — but that call's internal time.sleep() raced
    against the cookie component's own rerun, and whichever finished second
    silently won, sometimes dropping the navigation entirely with no error.
    Now login/signup just stash the user id here and navigate immediately;
    the actual (timing-sensitive) cookie write happens on the destination
    page's first render instead, with no navigation left to race against.
    """
    pending_user_id = st.session_state.pop("_pending_remember_user_id", None)
    if pending_user_id:
        set_remember_cookie(pending_user_id)
