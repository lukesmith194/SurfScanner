from pathlib import Path

import streamlit as st
from PIL import Image

import nav_pages
from header import render_user_indicator
from spots import SPOTS

# Absolute, not "../images" — that was relative to the process's current
# working directory, which is trip_planner/ locally (so it happened to
# work) but the repo root on Streamlit Cloud, breaking the path there.
IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "images"


def app():
    render_user_indicator()
    st.title("SurfScanner")
    st.write(
        "Welcome to SurfScanner, the perfect platform for surfers to plan "
        "their next surf trip!"
    )
    st.image(Image.open(IMAGES_DIR / "tauro4.jpeg"), width="stretch")

    st.markdown(
        f"This covers {len(SPOTS)} surf spots across Portugal, Spain (mainland, "
        "Basque Country and the Canary Islands), the UK and Ireland — picked because "
        "we have solid historical wave and wind data for each of them."
    )

    # --- Primary calls to action: Trip Planner + Community are the product. ---
    st.header("Ready to get out there?", text_alignment="center")

    cta_col1, cta_col2 = st.columns(2, gap="large")

    with cta_col1:
        with st.container(border=True):
            st.markdown("### :material/luggage: Plan your trip →")
            st.badge("Start here", icon=":material/arrow_forward:", color="blue")
            st.write(
                "Tell us your dates, level, departure city and budget — we'll "
                "rank every spot for your trip, with an estimated cost in euros."
            )
            st.page_link(
                nav_pages.trip_planner_page,
                label="Start planning",
                icon=":material/luggage:",
                width="stretch",
            )

    with cta_col2:
        with st.container(border=True):
            st.markdown("### :material/groups: Join the community →")
            st.badge("Popular", icon=":material/favorite:", color="orange")
            st.write(
                "Swap trip reports, tips and photos with other surfers, and see "
                "where the community is heading next."
            )
            st.page_link(
                nav_pages.community_page,
                label="Explore Community",
                icon=":material/groups:",
                width="stretch",
            )

    st.caption("Also available: reference material to help you choose a spot.")
    st.markdown(
        f"- **Spot info** — browse the {len(SPOTS)} spots, what they're like and who they suit.\n"
        "- **Historical** — compare wave height and wind trends across spots over the year.\n"
        "- **Predictions** — check the typical wave/wind conditions at one spot for your travel dates."
    )
    st.caption(
        "Conditions shown throughout are historical averages for the same time "
        "of year, not a live weather forecast."
    )
