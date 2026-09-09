from pathlib import Path

import streamlit as st
from PIL import Image

from spots import SPOTS

# Absolute, not "../images" — that was relative to the process's current
# working directory, which is trip_planner/ locally (so it happened to
# work) but the repo root on Streamlit Cloud, breaking the path there.
IMAGES_DIR = Path(__file__).resolve().parent.parent.parent / "images"


def app():
    st.title("SurfScanner")
    st.write(
        "Welcome to SurfScanner, the perfect platform for surfers to plan "
        "their next surf trip!"
    )
    st.image(Image.open(IMAGES_DIR / "tauro4.jpeg"), width="stretch")
    st.write(
        f"This covers {len(SPOTS)} surf spots across Portugal, Spain (mainland, "
        "Basque Country and the Canary Islands), the UK and Ireland — picked because "
        "we have solid historical wave and wind data for each of them."
    )

    st.subheader("What you can do here")
    st.markdown(
        f"- **Spot info** — browse the {len(SPOTS)} spots, what they're like and who they suit.\n"
        "- **Historical** — compare wave height and wind trends across spots over the year.\n"
        "- **Predictions** — check the typical wave/wind conditions at one spot for your travel dates.\n"
        "- **Trip Planner** — tell us your dates, level, departure city and budget, and we'll "
        "rank all the spots for your trip, with an estimated cost in euros."
    )
    st.caption(
        "Conditions shown throughout are historical averages for the same time "
        "of year, not a live weather forecast."
    )
