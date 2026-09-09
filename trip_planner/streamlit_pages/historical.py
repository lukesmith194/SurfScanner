import pandas as pd
import plotly.express as px
import streamlit as st

import spot_insights as si
from spots import SPOTS


def _map_section():
    st.write("### Spot locations")
    st.caption(
        "Click a spot on the map to see its best months by level, and filter "
        "the charts below to just that spot."
    )

    map_df = pd.DataFrame(
        [{"Spot": s.name, "Country": s.country, "lat": s.lat, "lon": s.lon} for s in SPOTS]
    )
    fig = px.scatter_map(
        map_df, lat="lat", lon="lon", hover_name="Spot",
        custom_data=["Spot"], color_discrete_sequence=["#e34234"],
        center={"lat": 40, "lon": -12}, zoom=2.7, height=450,
    )
    fig.update_traces(marker={"size": 14}, hovertemplate="<b>%{hovertext}</b><extra></extra>")
    fig.update_layout(margin={"l": 0, "r": 0, "t": 0, "b": 0})

    event = st.plotly_chart(
        fig, width="stretch", on_select="rerun", selection_mode="points", key="spot_map"
    )

    points = event.selection.points if event and event.selection else []
    if not points:
        st.info("No spot selected yet — click a marker above.")
        return None

    selected_name = points[0]["customdata"][0]
    spot = next(s for s in SPOTS if s.name == selected_name)

    with st.container(border=True):
        st.write(f"#### {spot.name} — {spot.country}")
        st.write(spot.blurb)
        for bm in si.best_months_by_level(spot):
            months = ", ".join(bm.months) if bm.months else "Not typically suitable"
            st.write(f"**{bm.level}:** {months}")

    return spot


def _single_spot_charts(spot):
    st.write(f"### {spot.name} — average wave height by month")
    wave = si.monthly_wave_height(spot).reindex(range(1, 13))
    wave_df = pd.DataFrame({"Month": si.MONTH_NAMES, "Wave height (ft)": wave.values})
    fig_wave = px.bar(wave_df, x="Month", y="Wave height (ft)")
    fig_wave.update_traces(hovertemplate="%{x}<br>%{y:.1f} ft<extra></extra>")
    st.plotly_chart(fig_wave, width="stretch")

    st.write(f"### {spot.name} — average wind speed by month")
    df = pd.read_csv(si.CSV_DIR / spot.wind_csv, parse_dates=["ds"])
    df["month"] = df["ds"].dt.month
    wind = df.groupby("month")["y"].mean().reindex(range(1, 13))
    wind_df = pd.DataFrame({"Month": si.MONTH_NAMES, "Wind speed (km/h)": wind.values})
    fig_wind = px.bar(wind_df, x="Month", y="Wind speed (km/h)")
    fig_wind.update_traces(hovertemplate="%{x}<br>%{y:.0f} km/h<extra></extra>")
    st.plotly_chart(fig_wind, width="stretch")


def _all_spots_charts():
    st.write("### Average wave height by month")
    wave_table = si.all_spots_monthly_wave_table()
    fig_wave = px.imshow(
        wave_table, color_continuous_scale="Blues", aspect="auto",
        labels={"x": "Month", "y": "Spot", "color": "Wave height (ft)"},
        text_auto=".1f",
    )
    fig_wave.update_layout(height=450)
    st.plotly_chart(fig_wave, width="stretch")
    st.caption(
        "Nazaré's winter big-wave season and the calmer Gran Canaria spots "
        "(El Fronton, Mosca Point, Tauro) show up clearly here."
    )

    st.write("### Average wind speed by month")
    wind_table = si.all_spots_monthly_wind_table()
    fig_wind = px.imshow(
        wind_table, color_continuous_scale="Greens", aspect="auto",
        labels={"x": "Month", "y": "Spot", "color": "Wind speed (km/h)"},
        text_auto=".0f",
    )
    fig_wind.update_layout(height=450)
    st.plotly_chart(fig_wind, width="stretch")


def app():
    st.write("## Historical conditions")

    selected_spot = _map_section()

    if selected_spot:
        _single_spot_charts(selected_spot)
    else:
        _all_spots_charts()
