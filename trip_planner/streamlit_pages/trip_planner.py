import datetime

import pandas as pd
import streamlit as st

import social
from accommodation import accommodation_options
from boards import BOARD_TYPES
from flights import travel_options
from recommender import recommend
from spots import DEPARTURE_AIRPORTS, DEPARTURE_CITIES
from header import render_user_indicator

# Material Symbols used per travel mode, so the "Getting there" list reads at
# a glance. Names validated against streamlit/material_icon_names.py.
TRAVEL_MODE_ICONS = {"drive": ":material/directions_car:", "fly": ":material/flight:"}

# flights.py and accommodation.py build their labels with emoji/arrow
# decoration of their own. Those modules belong to other pages too, so
# rather than editing them, strip the decoration here at render time and let
# the Material icon on each button carry the same meaning — otherwise every
# row shows both (e.g. "✈️ Fly DUB → SNN" next to a flight icon).
LABEL_DECORATION = ("✈️", "🚗", "🚆", "🏄", "🏠", "↗")


def _clean_label(label: str) -> str:
    """The label text with leading/trailing emoji and ↗ markers removed."""
    cleaned = label.strip()
    changed = True
    while changed:
        changed = False
        for token in LABEL_DECORATION:
            if cleaned.startswith(token):
                cleaned = cleaned[len(token) :].strip()
                changed = True
            if cleaned.endswith(token):
                cleaned = cleaned[: -len(token)].strip()
                changed = True
    return cleaned


def app():
    render_user_indicator()
    st.title("Trip planner", icon=":material/luggage:")
    st.write(
        "Pick your dates, level, home city and budget, and we'll rank the "
        "European spots for your trip, with an estimated cost in euros."
    )

    levels = ["Beginner", "Intermediate", "Advanced"]
    departure_options = list(DEPARTURE_CITIES.keys())
    level_index = 1
    departure_index = 0

    user_id = st.session_state.get("user_id")
    profile_user = social.get_user(user_id) if user_id else None
    if profile_user is not None:
        if profile_user.surf_level in levels:
            level_index = levels.index(profile_user.surf_level)
        if profile_user.home_city in departure_options:
            departure_index = departure_options.index(profile_user.home_city)

    board_type_index = 0
    if profile_user is not None and profile_user.board_type in BOARD_TYPES:
        board_type_index = BOARD_TYPES.index(profile_user.board_type)

    # The whole form lives in one bordered card so the inputs read as a single
    # unit against the result cards below. At layout="wide" the four
    # dates/dropdowns fit comfortably on one row, which keeps the form to two
    # rows instead of six stacked full-width widgets.
    today = datetime.date.today()
    with st.container(border=True):
        st.markdown(":material/tune: **Your trip**")
        date_col, end_col, from_col, board_col = st.columns(4)
        with date_col:
            start_date = st.date_input("Trip start", today + datetime.timedelta(days=30))
        with end_col:
            end_date = st.date_input(
                "Trip end",
                max(today + datetime.timedelta(days=37), start_date + datetime.timedelta(days=7)),
                min_value=start_date,
            )
        with from_col:
            departure = st.selectbox("Departing from", departure_options, index=departure_index)
        with board_col:
            board_type = st.selectbox("Preferred board type", BOARD_TYPES, index=board_type_index)

        level_col, budget_col = st.columns([1, 2], vertical_alignment="top")
        with level_col:
            # Three options, so a segmented control beats a dropdown (all
            # choices visible). required=True keeps a level always selected —
            # the recommender has no meaning for "no level".
            level = st.segmented_control(
                "Your surfing level",
                levels,
                default=levels[level_index],
                required=True,
            )
        with budget_col:
            budget_eur = st.slider(
                "Total budget for the trip (€, flights + stay)", 100, 2000, 600, step=50
            )

        # Plain button rather than st.form_submit_button — the date fields need
        # to react to each other live (min_value above), which st.form doesn't
        # allow (form widgets only sync on submit). st.button only returns True
        # on the exact rerun it's clicked, and any later interaction in the
        # results below (Share, travel/accommodation buttons) triggers its own
        # rerun where that would go back to False — persisting a "show results"
        # flag in session_state keeps results (and those buttons) alive across
        # such reruns.
        if st.button("Find my spots", type="primary", icon=":material/travel_explore:"):
            st.session_state["trip_planner_submitted"] = True

    if not st.session_state.get("trip_planner_submitted"):
        return

    results = recommend(
        start_date=start_date,
        end_date=end_date,
        level=level,
        departure=DEPARTURE_CITIES[departure],
        budget_eur=budget_eur,
    )

    if not results:
        st.warning("No historical data available for those dates.", icon=":material/warning:")
        return

    st.subheader("Recommended spots, closest first", icon=":material/explore:")
    st.caption(
        "Sorted by distance from " + departure + ", then by cheapest estimated "
        "trip cost — spots more than 10% over your budget are left out entirely."
    )
    for rank, rec in enumerate(results, start=1):
        with st.container(border=True):
            over_budget = rec.total_cost_eur > budget_eur

            # Rank as a badge rather than "1." prose — it reads as a ranking
            # marker and keeps the spot name as the visual anchor of the card.
            with st.container(horizontal=True, vertical_alignment="center"):
                st.badge(f"#{rank}", color="primary")
                st.markdown(
                    f"#### {rec.spot.name} · {rec.spot.country}",
                    width="content",
                )
            st.write(rec.spot.blurb)

            # Money on the left (the number people actually decide on), surf
            # conditions as a 2x2 grid on the right. At wide layout this reads
            # far better than four cramped metric columns in a single row.
            cost_col, conditions_col = st.columns([1, 2], gap="medium")
            with cost_col:
                cost_parts = []
                if rec.flight_eur > 0:
                    cost_parts.append(f"€{rec.flight_eur:,.0f} flights (round trip est.)")
                if rec.ground_eur > 0:
                    cost_parts.append(f"€{rec.ground_eur:,.0f} ground travel (drive/train est.)")
                cost_parts.append(
                    f"€{rec.accommodation_eur:,.0f} accommodation/food for {rec.nights} night(s)"
                )
                # The cost card carries the breakdown on its face as well as
                # in the metric's tooltip — this is the number people commit
                # money against, and it fills the card that height="stretch"
                # squares up against the 2x2 conditions grid beside it.
                with st.container(border=True, height="stretch"):
                    st.metric(
                        "Estimated total cost",
                        f"€{rec.total_cost_eur:,.0f}",
                        help=" + ".join(cost_parts),
                        icon=":material/payments:",
                    )
                    if over_budget:
                        st.badge("Over budget", icon=":material/warning:", color="orange")
                    for part in cost_parts:
                        st.caption(part)

            with conditions_col:
                top_left, top_right = st.columns(2)
                top_left.metric(
                    "Distance from " + departure,
                    f"{rec.distance_km:,.0f} km",
                    icon=":material/straighten:",
                    border=True,
                )
                top_right.metric(
                    "Suitability for your level",
                    f"{rec.level_score:.0%}",
                    icon=":material/surfing:",
                    border=True,
                )
                bottom_left, bottom_right = st.columns(2)
                bottom_left.metric(
                    "Avg wave height",
                    f"{rec.avg_wave_ft:.1f} ft",
                    icon=":material/waves:",
                    border=True,
                )
                bottom_right.metric(
                    "Avg wind speed",
                    f"{rec.avg_wind_kmh:.0f} km/h",
                    icon=":material/air:",
                    border=True,
                )

            st.caption(f"Matched to your {level.lower()} level, budget of €{budget_eur:,.0f}")

            # Travel and stay are the two booking decisions — side by side at
            # wide layout so a whole spot fits in one screenful.
            travel_col, stay_col = st.columns(2, gap="medium")
            with travel_col:
                st.markdown(":material/route: **Getting there**")
                options = travel_options(
                    departure_name=departure,
                    departure_coords=DEPARTURE_CITIES[departure],
                    origin_iata=DEPARTURE_AIRPORTS[departure],
                    spot=rec.spot,
                    start_date=start_date,
                    end_date=end_date,
                )
                for option in options:
                    mode_icon = TRAVEL_MODE_ICONS.get(option.mode, ":material/signpost:")
                    if option.mode == "drive":
                        st.markdown(f"{mode_icon} {_clean_label(option.label)}")
                        st.caption(option.detail)
                    else:
                        st.link_button(
                            f"{_clean_label(option.label)} on Skyscanner",
                            option.url,
                            icon=mode_icon,
                        )
                        st.caption(option.detail)

                    if option.ground_travel_url:
                        st.link_button(
                            "Compare trains, buses & car rental on Rome2Rio",
                            option.ground_travel_url,
                            icon=":material/train:",
                        )

            with stay_col:
                st.markdown(":material/hotel: **Where to stay**")
                for stay in accommodation_options(rec.spot, start_date, end_date):
                    st.link_button(
                        _clean_label(stay.label), stay.url, icon=":material/bed:"
                    )
                    if stay.caveat:
                        st.caption(stay.caveat)

            user_id = st.session_state.get("user_id")
            if user_id:
                if st.button(
                    "Share this trip to Community",
                    icon=":material/campaign:",
                    key=f"share_{rec.spot.name}_{rank}",
                ):
                    social.create_post(
                        author_id=user_id,
                        spot_name=rec.spot.name,
                        start_date=start_date,
                        end_date=end_date,
                        level=level,
                        note="Shared from Trip Planner",
                        board_type=board_type,
                        total_cost_eur=rec.total_cost_eur,
                        distance_km=rec.distance_km,
                        nights=rec.nights,
                    )
                    st.success("Posted to Community!", icon=":material/check_circle:")
            else:
                st.caption("Log in on the Account page to share this trip with the Community.")

    with st.container(border=True):
        st.markdown(":material/map: **Spot locations**")
        map_df = pd.DataFrame([{"lat": r.spot.lat, "lon": r.spot.lon} for r in results])
        st.map(map_df)

    st.caption(
        "Next up: local recommendations (food, rentals, lessons) will plug "
        "into this same trip once that integration exists."
    )
