import datetime

import streamlit as st

import social
from spots import SPOTS
from header import render_user_indicator

SPOT_NAMES = [s.name for s in SPOTS]

REACTION_EMOJI = ["🤙", "🔥", "😂", "😮", "👍"]


def _post_form(user_id: int):
    user = social.get_user(user_id)
    st.write("**Plan a trip and post it**")

    # Dates live outside the form so the End field can react immediately to
    # the Start field via min_value — st.form only syncs widget values on
    # submit, so it can't restrict End's calendar live while still inside one.
    today = datetime.date.today()
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start", today + datetime.timedelta(days=14), key="post_start")
    with col2:
        end_date = st.date_input(
            "End",
            max(today + datetime.timedelta(days=17), start_date + datetime.timedelta(days=3)),
            min_value=start_date,
            key="post_end",
        )

    with st.form("new_post_form", clear_on_submit=True):
        spot_name = st.selectbox("Spot", SPOT_NAMES)
        note = st.text_input("Anything else? (optional)", max_chars=280)
        submitted = st.form_submit_button("Post to feed")

    if submitted:
        social.create_post(user_id, spot_name, start_date, end_date, user.surf_level, note)
        st.success("Posted!")
        st.rerun()


def _feed(user_id: int):
    posts = social.feed_for(user_id)
    st.write("**Feed**")
    if not posts:
        st.caption("No posts yet — post your own trip above, or follow other surfers below.")
        return

    for post in posts:
        with st.container(border=True):
            st.markdown(f"**{post.author_name}** · {post.author_home_city}")
            st.write(
                f"Planning **{post.spot_name}**, "
                f"{post.start_date:%b %d} – {post.end_date:%b %d} · {post.level}"
            )
            if post.note:
                st.write(post.note)

            if post.total_cost_eur is not None:
                details = []
                if post.board_type:
                    details.append(f"🏄 {post.board_type}")
                if post.total_cost_eur is not None:
                    details.append(f"€{post.total_cost_eur:,.0f} total")
                if post.distance_km is not None:
                    details.append(f"{post.distance_km:,.0f} km away")
                if post.nights is not None:
                    details.append(f"{post.nights} night(s)")
                st.caption(" · ".join(details))

            reaction_summary = social.reaction_summary(post.post_id, user_id)
            reaction_cols = st.columns(len(REACTION_EMOJI))
            for emoji, col in zip(REACTION_EMOJI, reaction_cols):
                count, viewer_reacted = reaction_summary.get(emoji, (0, False))
                label = f"{emoji} {count}" if count else emoji
                with col:
                    if st.button(
                        label,
                        key=f"react_{emoji}_{post.post_id}",
                        type="primary" if viewer_reacted else "secondary",
                    ):
                        social.toggle_reaction(post.post_id, user_id, emoji)
                        st.rerun()

            col1, col2 = st.columns([1, 1])
            with col1:
                if post.is_own_post:
                    st.caption(f"{post.interest_count} interested")
                else:
                    join_label = "✅ Interested" if post.viewer_is_interested else "🤙 I'm interested"
                    if st.button(f"{join_label} ({post.interest_count})", key=f"join_{post.post_id}"):
                        social.toggle_interest(post.post_id, user_id)
                        st.rerun()
            with col2:
                if not post.is_own_post:
                    following = post.author_id in social.following_ids(user_id)
                    if following:
                        if st.button("Following ✓", key=f"unfollow_{post.author_id}_{post.post_id}"):
                            social.unfollow(user_id, post.author_id)
                            st.rerun()
                    else:
                        if st.button("Follow", key=f"follow_{post.author_id}_{post.post_id}"):
                            social.follow(user_id, post.author_id)
                            st.rerun()

            all_comments = social.comments_for(post.post_id)
            visible_comments, hidden_comments = all_comments[:2], all_comments[2:]
            for comment in visible_comments:
                st.markdown(f"**{comment.author_name}:** {comment.body}")

            if hidden_comments:
                with st.expander(f"💬 View all {post.comment_count} comments"):
                    for comment in hidden_comments:
                        st.markdown(f"**{comment.author_name}:** {comment.body}")
                    with st.form(f"comment_form_{post.post_id}", clear_on_submit=True):
                        body = st.text_input(
                            "Add a comment", max_chars=280, label_visibility="collapsed"
                        )
                        if st.form_submit_button("Comment"):
                            social.add_comment(post.post_id, user_id, body)
                            st.rerun()
            else:
                with st.form(f"comment_form_{post.post_id}", clear_on_submit=True):
                    body = st.text_input("Add a comment", max_chars=280, label_visibility="collapsed")
                    if st.form_submit_button("Comment"):
                        social.add_comment(post.post_id, user_id, body)
                        st.rerun()


def _find_surfers(user_id: int):
    st.write("**Find surfers**")
    others = social.list_other_users(user_id)
    if not others:
        st.caption("No other surfers on the platform yet.")
        return

    followed = social.following_ids(user_id)
    for other in others:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{other.display_name}** — {other.home_city}, {other.surf_level}")
            with col2:
                if other.id in followed:
                    if st.button("Following ✓", key=f"unfollow_list_{other.id}"):
                        social.unfollow(user_id, other.id)
                        st.rerun()
                else:
                    if st.button("Follow", key=f"follow_list_{other.id}"):
                        social.follow(user_id, other.id)
                        st.rerun()


def app():
    render_user_indicator()
    st.write("## Community")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.info("Log in or create an account on the Account page to post trips and follow surfers.")
        return

    _post_form(user_id)
    st.divider()
    _feed(user_id)
    st.divider()
    _find_surfers(user_id)
