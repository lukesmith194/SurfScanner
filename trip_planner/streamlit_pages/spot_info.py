import datetime
import json
from pathlib import Path

import streamlit as st
from PIL import Image

import spot_insights as si
from spots import SPOTS
from header import render_user_indicator

# Absolute, not "../images" — that was relative to the process's current
# working directory, which is trip_planner/ locally (so it happened to work)
# but the repo root on Streamlit Cloud, breaking the path there.
IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "images"
CREDITS_PATH = Path(__file__).resolve().parent.parent / "image_credits.json"
IMAGE_CREDITS = json.loads(CREDITS_PATH.read_text()) if CREDITS_PATH.exists() else {}
CURRENT_MONTH = datetime.date.today().month


def base_country(country: str) -> str:
    """Normalize a spot's `country` field to its top-level country name.

    e.g. "Spain (Basque Country)" -> "Spain", "UK (Cornwall)" -> "UK".
    """
    return country.split("(")[0].strip()


def render_spot_card(spot):
    with st.container(border=True):
        st.subheader(spot.name, icon=":material/surfing:")
        st.caption(f":material/place: {spot.country}")

        if spot.image:
            try:
                st.image(Image.open(IMAGES_DIR / spot.image), width="stretch")
                credit = IMAGE_CREDITS.get(Path(spot.image).stem)
                if credit:
                    st.caption(f"Photo: {credit['artist']} · {credit['license']} · Wikimedia Commons")
            except FileNotFoundError:
                pass

        st.write(spot.blurb)

        if spot.recommended_boards:
            st.caption(f":material/kayaking: Recommended board: **{', '.join(spot.recommended_boards)}**")

        with st.container(horizontal=True):
            if spot.learn_more_url:
                st.link_button("Learn more", spot.learn_more_url, icon=":material/info:")
            if spot.forecast_url:
                st.link_button("Check live forecast", spot.forecast_url, icon=":material/open_in_new:")

        temp_c, wetsuit = si.current_conditions_summary(spot, CURRENT_MONTH)
        col1, col2 = st.columns(2)
        col1.metric("Water temp now", f"{temp_c:.0f}°C")
        with col2:
            st.caption("Recommended wetsuit")
            st.write(f"**{wetsuit}**")

        with st.expander("Water temp & wetsuit by month", icon=":material/water_drop:"):
            temps = si.monthly_water_temp(spot)
            for month_num, month_name in enumerate(si.MONTH_NAMES, start=1):
                t = temps.get(month_num)
                if t is not None:
                    st.write(f"**{month_name}:** {t:.0f}°C — {si.wetsuit_for_temp(t)}")

        with st.expander("Best months by level", icon=":material/calendar_month:"):
            for bm in si.best_months_by_level(spot):
                months = ", ".join(bm.months) if bm.months else "Not typically suitable"
                st.write(f"- **{bm.level}:** {months}")


def app():
    render_user_indicator()
    st.write(f"## The {len(SPOTS)} spots")
    st.write(
        "Our Europe spot list — each one has historical wave and wind data "
        "backing its recommendations."
    )

    with st.container(border=True):
        search = st.text_input(
            "Search spots by name or country", icon=":material/search:"
        )

        countries = sorted({base_country(spot.country) for spot in SPOTS})
        continents = sorted({spot.continent for spot in SPOTS})
        col_country, col_continent = st.columns(2)
        with col_country:
            selected_countries = st.multiselect("Filter by country", countries)
        with col_continent:
            selected_continents = st.multiselect("Filter by continent", continents)

        with st.expander("Spots by country", icon=":material/map:"):
            for country in countries:
                names = [s.name for s in SPOTS if base_country(s.country) == country]
                st.write(f"**{country}** ({len(names)}): {', '.join(names)}")

    def matches(spot) -> bool:
        if search:
            needle = search.lower()
            if needle not in spot.name.lower() and needle not in spot.country.lower():
                return False
        if selected_countries and base_country(spot.country) not in selected_countries:
            return False
        if selected_continents and spot.continent not in selected_continents:
            return False
        return True

    filtered_spots = [spot for spot in SPOTS if matches(spot)]
    if not filtered_spots:
        st.info("No spots match your search/filters.")

    st.caption(f"Showing {len(filtered_spots)} of {len(SPOTS)} spots")

    cols = st.columns(2)
    for i, spot in enumerate(filtered_spots):
        with cols[i % 2]:
            render_spot_card(spot)
