import datetime

import streamlit as st

import social
from spots import SPOTS
from header import render_user_indicator

SPOT_NAMES = [s.name for s in SPOTS]

REACTION_EMOJI = ["🤙", "🔥", "😂", "😮", "👍"]


def _post_form(user_id: int):
    user = social.get_user(user_id)

    with st.container(border=True):
        st.subheader("Plan a trip", icon=":material/edit_calendar:")
        st.caption("Post where you're heading and let other surfers join you.")

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

        # border=False: the surrounding card already groups these fields, so the
        # form's own border would double up.
        with st.form("new_post_form", clear_on_submit=True, border=False):
            spot_name = st.selectbox("Spot", SPOT_NAMES)
            note = st.text_input(
                "Anything else? (optional)", max_chars=280, placeholder="Add a note for the feed"
            )
            submitted = st.form_submit_button(
                "Post to feed", type="primary", icon=":material/send:"
            )

    if submitted:
        social.create_post(user_id, spot_name, start_date, end_date, user.surf_level, note)
        # A toast rather than st.success: the immediate rerun below would wipe an
        # in-page success box before it's ever seen, whereas toasts survive it.
        st.toast("Posted to your feed", icon=":material/check_circle:")
        st.rerun()


def _snapshot_badges(post) -> str:
    """The Trip Planner snapshot line as a compact badge row.

    Badge colors come from the theme's semantic tokens (see .streamlit/config.toml),
    so nothing here hardcodes a hex value.
    """
    badges = []
    if post.board_type:
        badges.append(f":blue-badge[:material/surfing: {post.board_type}]")
    if post.total_cost_eur is not None:
        badges.append(f":green-badge[:material/payments: €{post.total_cost_eur:,.0f} total]")
    if post.distance_km is not None:
        badges.append(f":violet-badge[:material/route: {post.distance_km:,.0f} km away]")
    if post.nights is not None:
        badges.append(f":gray-badge[:material/king_bed: {post.nights} night(s)]")
    return " ".join(badges)


def _comment_form(post_id: int, user_id: int):
    """Inline 'add a comment' composer — one row, no form border."""
    with st.form(f"comment_form_{post_id}", clear_on_submit=True, border=False):
        with st.container(horizontal=True, vertical_alignment="bottom"):
            body = st.text_input(
                "Add a comment",
                max_chars=280,
                label_visibility="collapsed",
                placeholder="Add a comment",
            )
            if st.form_submit_button("Send", icon=":material/send:"):
                social.add_comment(post_id, user_id, body)
                st.rerun()


def _comment_line(comment) -> None:
    st.markdown(f"**{comment.author_name}** {comment.body}")


def _post_card(post, user_id: int) -> None:
    with st.container(border=True):
        # Author on the left, follow control on the right — the familiar social
        # card header, which also gets Follow out of the action row below.
        author_col, follow_col = st.columns([3, 1], vertical_alignment="center")
        with author_col:
            st.markdown(f"**{post.author_name}**")
            st.caption(f":material/place: {post.author_home_city}")
        with follow_col:
            if not post.is_own_post:
                with st.container(horizontal=True, horizontal_alignment="right"):
                    following = post.author_id in social.following_ids(user_id)
                    if following:
                        if st.button(
                            "Following",
                            key=f"unfollow_{post.author_id}_{post.post_id}",
                            icon=":material/how_to_reg:",
                            type="tertiary",
                        ):
                            social.unfollow(user_id, post.author_id)
                            st.rerun()
                    else:
                        if st.button(
                            "Follow",
                            key=f"follow_{post.author_id}_{post.post_id}",
                            icon=":material/person_add:",
                        ):
                            social.follow(user_id, post.author_id)
                            st.rerun()

        st.markdown(f"##### {post.spot_name}")
        st.markdown(
            f":blue-badge[:material/date_range: {post.start_date:%b %d} – {post.end_date:%b %d}] "
            f":gray-badge[:material/signal_cellular_alt: {post.level}]"
        )

        if post.note:
            st.write(post.note)

        if post.total_cost_eur is not None:
            st.markdown(_snapshot_badges(post))

        # One reaction chip per emoji, in a content-width row. Kept as individual
        # buttons rather than st.pills: each emoji is its own independent toggle
        # carrying its own count and "you reacted" state, which a single
        # multi-select widget can't show per option — and this reads at a glance
        # like the reaction bars people already know. The emoji stay real emoji
        # (they're the content, not icon chrome); only the surrounding controls
        # use Material icons.
        reaction_summary = social.reaction_summary(post.post_id, user_id)
        with st.container(horizontal=True, gap="small", vertical_alignment="center"):
            for emoji in REACTION_EMOJI:
                count, viewer_reacted = reaction_summary.get(emoji, (0, False))
                label = f"{emoji} {count}" if count else emoji
                if st.button(
                    label,
                    key=f"react_{emoji}_{post.post_id}",
                    type="primary" if viewer_reacted else "secondary",
                ):
                    social.toggle_reaction(post.post_id, user_id, emoji)
                    st.rerun()

            if post.is_own_post:
                st.caption(f"{post.interest_count} interested")
            elif post.viewer_is_interested:
                if st.button(
                    f"Interested ({post.interest_count})",
                    key=f"join_{post.post_id}",
                    icon=":material/check_circle:",
                    type="primary",
                ):
                    social.toggle_interest(post.post_id, user_id)
                    st.rerun()
            else:
                if st.button(
                    f"I'm interested ({post.interest_count})",
                    key=f"join_{post.post_id}",
                    icon=":material/front_hand:",
                ):
                    social.toggle_interest(post.post_id, user_id)
                    st.rerun()

        all_comments = social.comments_for(post.post_id)
        visible_comments, hidden_comments = all_comments[:2], all_comments[2:]
        if visible_comments:
            with st.container(gap=None):
                for comment in visible_comments:
                    _comment_line(comment)

        if hidden_comments:
            with st.expander(
                f"All {post.comment_count} comments", icon=":material/forum:"
            ):
                with st.container(gap=None):
                    for comment in hidden_comments:
                        _comment_line(comment)
                _comment_form(post.post_id, user_id)
        else:
            _comment_form(post.post_id, user_id)


def _feed(user_id: int):
    st.subheader("Feed", icon=":material/waves:")
    posts = social.feed_for(user_id)
    if not posts:
        st.caption("No posts yet — post your own trip, or follow other surfers to see theirs.")
        return

    for post in posts:
        _post_card(post, user_id)


def _find_surfers(user_id: int):
    with st.container(border=True):
        st.subheader("Find surfers", icon=":material/groups:")
        others = social.list_other_users(user_id)
        if not others:
            st.caption("No other surfers on the platform yet.")
            return

        st.caption("Follow someone to see their trips in your feed.")
        followed = social.following_ids(user_id)
        for other in others:
            name_col, action_col = st.columns([2, 1], vertical_alignment="center")
            with name_col:
                st.markdown(f"**{other.display_name}**")
                st.caption(f"{other.home_city} · {other.surf_level}")
            with action_col:
                with st.container(horizontal=True, horizontal_alignment="right"):
                    if other.id in followed:
                        if st.button(
                            "Following",
                            key=f"unfollow_list_{other.id}",
                            icon=":material/how_to_reg:",
                            type="tertiary",
                        ):
                            social.unfollow(user_id, other.id)
                            st.rerun()
                    else:
                        if st.button(
                            "Follow",
                            key=f"follow_list_{other.id}",
                            icon=":material/person_add:",
                        ):
                            social.follow(user_id, other.id)
                            st.rerun()


def app():
    render_user_indicator()
    st.title("Community", icon=":material/groups:")

    user_id = st.session_state.get("user_id")
    if not user_id:
        st.info(
            "Log in or create an account on the Account page to post trips and follow surfers.",
            icon=":material/person:",
        )
        return

    # layout="wide" is set globally in main.py, so the page gets a two-column
    # reading layout: the feed keeps the wide, primary column, while composing a
    # trip and finding surfers sit together in a narrower right-hand rail.
    feed_col, rail_col = st.columns([2, 1], gap="medium")
    with feed_col:
        _feed(user_id)
    with rail_col:
        _post_form(user_id)
        _find_surfers(user_id)
