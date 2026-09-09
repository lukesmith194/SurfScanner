import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import spot_insights as si
from recommender import date_range_month_days, load_series
from spots import SPOTS

SPOT_BY_NAME = {s.name: s for s in SPOTS}


def _compass_figure(wind_deg: float, swell_deg: float, offshore_deg: float, wind_color: str) -> go.Figure:
    """N-up compass: shaded offshore/onshore halves for reference, a needle
    for the average wind direction (colored by onshore/offshore type), and a
    marker for the average swell direction.
    """
    fig = go.Figure()
    fig.add_trace(go.Barpolar(
        r=[1], theta=[offshore_deg], width=[90], marker_color="green", opacity=0.15,
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Barpolar(
        r=[1], theta=[(offshore_deg + 180) % 360], width=[90], marker_color="red", opacity=0.10,
        hoverinfo="skip", showlegend=False,
    ))
    fig.add_trace(go.Scatterpolar(
        r=[0, 1], theta=[wind_deg, wind_deg], mode="lines+markers",
        line={"color": wind_color, "width": 4}, marker={"size": [0, 12]},
        name="Wind", hovertemplate=f"Wind: {si.compass_label(wind_deg)}<extra></extra>",
    ))
    fig.add_trace(go.Scatterpolar(
        r=[0.75], theta=[swell_deg], mode="markers",
        marker={"size": 14, "symbol": "diamond", "color": "royalblue"},
        name="Swell", hovertemplate=f"Swell: {si.compass_label(swell_deg)}<extra></extra>",
    ))
    fig.update_layout(
        polar={
            "angularaxis": {
                "direction": "clockwise", "rotation": 90,
                "tickvals": [0, 45, 90, 135, 180, 225, 270, 315],
                "ticktext": ["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
            },
            "radialaxis": {"visible": False, "range": [0, 1]},
        },
        showlegend=True, legend={"orientation": "h", "y": -0.1},
        margin={"l": 30, "r": 30, "t": 30, "b": 30}, height=350,
    )
    return fig


def _daily_climatology(df: pd.DataFrame, ordered_month_days: list[str], value_name: str) -> pd.DataFrame:
    """Average value per calendar day of the trip, in trip date order (not
    alphabetical MM-DD order, which would misorder a trip spanning a year
    boundary, e.g. Dec 28 - Jan 3).
    """
    daily = df.groupby("month_day")["y"].mean()
    rows = []
    for month_day in ordered_month_days:
        if month_day in daily.index:
            month, day = month_day.split("-")
            label = datetime.date(2001, int(month), int(day)).strftime("%b %d")
            rows.append({"date": label, value_name: daily[month_day]})
    return pd.DataFrame(rows)


def app():
    st.write("## Predictions")
    st.write(
        "Pick a spot and your travel dates — we'll show the historical "
        "average wave height and wind speed for each day of your trip."
    )

    spot_name = st.selectbox("Spot", list(SPOT_BY_NAME.keys()))
    today = datetime.date.today()
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start date", today + datetime.timedelta(days=30))
    with col2:
        end_date = st.date_input(
            "End date",
            max(today + datetime.timedelta(days=37), start_date + datetime.timedelta(days=7)),
            min_value=start_date,
        )

    spot = SPOT_BY_NAME[spot_name]
    wave_df = load_series(spot.wave_csv)
    wind_df = load_series(spot.wind_csv)
    ordered_month_days = date_range_month_days(start_date, end_date)
    month_days = set(ordered_month_days)

    wave_hist = wave_df[wave_df["month_day"].isin(month_days)]
    wind_hist = wind_df[wind_df["month_day"].isin(month_days)]

    if wave_hist.empty:
        st.warning("No historical data for those dates.")
        return

    avg_wind_speed = wind_hist["y"].mean() if not wind_hist.empty else float("nan")
    swell_deg = si.swell_direction_for_range(spot, start_date, end_date)
    wind_deg = si.wind_direction_for_range(spot, start_date, end_date)
    wind_type, wind_color = si.classify_wind(wind_deg, avg_wind_speed, spot.offshore_deg)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg wave height", f"{wave_hist['y'].mean():.1f} ft")
    col2.metric("Predominant swell", si.compass_label(swell_deg))
    col3.metric("Avg wind speed", f"{avg_wind_speed:.0f} km/h" if not wind_hist.empty else "n/a")
    col4.metric("Predominant wind", si.compass_label(wind_deg))

    compass_col, box_col = st.columns([2, 1])
    with compass_col:
        st.plotly_chart(
            _compass_figure(wind_deg, swell_deg, spot.offshore_deg, wind_color),
            width="stretch",
        )
        st.caption(
            f"Green = offshore side, red = onshore side, at {spot.name} "
            f"(offshore blows from the {si.compass_label(spot.offshore_deg)})."
        )
    with box_col:
        box = {"green": st.success, "blue": st.info, "orange": st.warning, "red": st.error}[wind_color]
        box(f"**{wind_type}**\n\nAvg wind conditions for these dates.")

    st.write(f"### {spot_name} — day by day for your trip")

    wave_daily = _daily_climatology(wave_hist, ordered_month_days, "Wave height (ft)")
    fig_wave = px.bar(wave_daily, x="date", y="Wave height (ft)")
    fig_wave.update_layout(xaxis_title=None)
    fig_wave.update_traces(hovertemplate="%{x}<br>%{y:.1f} ft<extra></extra>")
    st.plotly_chart(fig_wave, width="stretch")

    wind_daily = _daily_climatology(wind_hist, ordered_month_days, "Wind speed (km/h)")
    fig_wind = px.bar(wind_daily, x="date", y="Wind speed (km/h)")
    fig_wind.update_layout(xaxis_title=None)
    fig_wind.update_traces(hovertemplate="%{x}<br>%{y:.0f} km/h<extra></extra>")
    st.plotly_chart(fig_wind, width="stretch")

    st.caption(
        "Each bar is the historical average for that calendar day — not a "
        "day-specific forecast."
    )
