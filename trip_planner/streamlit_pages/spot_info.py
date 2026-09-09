import datetime
import json
from pathlib import Path

import streamlit as st
from PIL import Image

import spot_insights as si
from spots import SPOTS

IMAGES_DIR = "../images"
CREDITS_PATH = Path(__file__).resolve().parent.parent / "image_credits.json"
IMAGE_CREDITS = json.loads(CREDITS_PATH.read_text()) if CREDITS_PATH.exists() else {}
CURRENT_MONTH = datetime.date.today().month


def app():
    st.write(f"## The {len(SPOTS)} spots")
    st.write(
        "Our Europe spot list — each one has historical wave and wind data "
        "backing its recommendations."
    )

    for spot in SPOTS:
        st.write(f"### {spot.name} — {spot.country}")
        if spot.image:
            try:
                st.image(Image.open(f"{IMAGES_DIR}/{spot.image}"), width="stretch")
                credit = IMAGE_CREDITS.get(Path(spot.image).stem)
                if credit:
                    st.caption(f"Photo: {credit['artist']} · {credit['license']} · Wikimedia Commons")
            except FileNotFoundError:
                pass

        st.write(spot.blurb)
        if spot.learn_more_url:
            st.markdown(f"[Learn more ↗]({spot.learn_more_url})")

        temp_c, wetsuit = si.current_conditions_summary(spot, CURRENT_MONTH)
        col1, col2 = st.columns(2)
        col1.metric("Water temp now", f"{temp_c:.0f}°C")
        with col2:
            st.caption("Recommended wetsuit")
            st.write(f"**{wetsuit}**")

        with st.expander("Water temp & wetsuit by month"):
            temps = si.monthly_water_temp(spot)
            for month_num, month_name in enumerate(si.MONTH_NAMES, start=1):
                t = temps.get(month_num)
                if t is not None:
                    st.write(f"**{month_name}:** {t:.0f}°C — {si.wetsuit_for_temp(t)}")

        st.write("**Best months by level**")
        for bm in si.best_months_by_level(spot):
            months = ", ".join(bm.months) if bm.months else "Not typically suitable"
            st.write(f"- **{bm.level}:** {months}")

        st.divider()
