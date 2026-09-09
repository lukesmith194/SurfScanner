import datetime

import pandas as pd
import streamlit as st

import social
from accommodation import accommodation_options
from flights import travel_options
from recommender import recommend
from spots import DEPARTURE_AIRPORTS, DEPARTURE_CITIES
from header import render_user_indicator


def app():
    render_user_indicator()
    st.write("## Trip Planner")
    st.write(
        "Pick your dates, level, home city and budget, and we'll rank the "
        "European spots for your trip, with an estimated cost in euros."
    )

    col1, col2 = st.columns(2)
    today = datetime.date.today()
    with col1:
        start_date = st.date_input("Trip start", today + datetime.timedelta(days=30))
    with col2:
        end_date = st.date_input(
            "Trip end",
            max(today + datetime.timedelta(days=37), start_date + datetime.timedelta(days=7)),
            min_value=start_date,
        )

    level = st.selectbox("Your surfing level", ["Beginner", "Intermediate", "Advanced"], index=1)
    departure = st.selectbox("Departing from", list(DEPARTURE_CITIES.keys()))
    budget_eur = st.slider("Total budget for the trip (€, flights + stay)", 100, 2000, 600, step=50)

    # Plain button rather than st.form_submit_button — the date fields need
    # to react to each other live (min_value above), which st.form doesn't
    # allow (form widgets only sync on submit). st.button only returns True
    # on the exact rerun it's clicked, and any later interaction in the
    # results below (Share, travel/accommodation buttons) triggers its own
    # rerun where that would go back to False — persisting a "show results"
    # flag in session_state keeps results (and those buttons) alive across
    # such reruns.
    if st.button("Find my spots"):
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
        st.warning("No historical data available for those dates.")
        return

    st.subheader("Recommended spots, closest first")
    st.caption(
        "Sorted by distance from " + departure + ", then by cheapest estimated "
        "trip cost — spots more than 10% over your budget are left out entirely."
    )
    for rank, rec in enumerate(results, start=1):
        with st.container(border=True):
            over_budget = rec.total_cost_eur > budget_eur
            st.markdown(f"### {rank}. {rec.spot.name} — {rec.spot.country}")
            st.write(rec.spot.blurb)

            metrics = st.columns(4)
            metrics[0].metric("Distance from " + departure, f"{rec.distance_km:,.0f} km")
            metrics[1].metric("Avg wave height", f"{rec.avg_wave_ft:.1f} ft")
            metrics[2].metric("Avg wind speed", f"{rec.avg_wind_kmh:.0f} km/h")
            metrics[3].metric("Suitability for your level", f"{rec.level_score:.0%}")

            cost_label = "Estimated total cost" + (" ⚠️ over budget" if over_budget else "")
            cost_parts = []
            if rec.flight_eur > 0:
                cost_parts.append(f"€{rec.flight_eur:,.0f} flights (round trip est.)")
            if rec.ground_eur > 0:
                cost_parts.append(f"€{rec.ground_eur:,.0f} ground travel (drive/train est.)")
            cost_parts.append(f"€{rec.accommodation_eur:,.0f} accommodation/food for {rec.nights} night(s)")
            st.metric(
                cost_label,
                f"€{rec.total_cost_eur:,.0f}",
                help=" + ".join(cost_parts),
            )
            st.caption(f"Matched to your {level.lower()} level, budget of €{budget_eur:,.0f}")

            st.markdown("**Getting there**")
            options = travel_options(
                departure_name=departure,
                departure_coords=DEPARTURE_CITIES[departure],
                origin_iata=DEPARTURE_AIRPORTS[departure],
                spot=rec.spot,
                start_date=start_date,
                end_date=end_date,
            )
            for option in options:
                if option.mode == "drive":
                    st.write(option.label)
                    st.caption(option.detail)
                else:
                    st.link_button(f"{option.label} on Skyscanner ↗", option.url)
                    st.caption(option.detail)

                if option.ground_travel_url:
                    st.link_button(
                        "🚆 Compare trains, buses & car rental on Rome2Rio ↗",
                        option.ground_travel_url,
                    )

            st.markdown("**Where to stay**")
            for stay in accommodation_options(rec.spot, start_date, end_date):
                st.link_button(stay.label, stay.url)
                if stay.caveat:
                    st.caption(stay.caveat)

            user_id = st.session_state.get("user_id")
            if user_id:
                if st.button("📣 Share this trip to Community", key=f"share_{rec.spot.name}_{rank}"):
                    social.create_post(
                        author_id=user_id,
                        spot_name=rec.spot.name,
                        start_date=start_date,
                        end_date=end_date,
                        level=level,
                        note="Shared from Trip Planner",
                    )
                    st.success("Posted to Community!")
            else:
                st.caption("Log in on the Account page to share this trip with the Community.")

    st.subheader("Spot locations")
    map_df = pd.DataFrame([{"lat": r.spot.lat, "lon": r.spot.lon} for r in results])
    st.map(map_df)

    st.caption(
        "Next up: local recommendations (food, rentals, lessons) will plug "
        "into this same trip once that integration exists."
    )
