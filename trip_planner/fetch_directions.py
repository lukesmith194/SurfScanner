"""One-off pull of real wind direction and swell direction for all 14 spots,
from the same Open-Meteo APIs already used for wave height/wind speed/water
temp. Needed for the Predictions page's onshore/offshore/cross-shore/glassy
classification and predominant swell direction.

Directions are circular (0-360°), so they're stored as raw hourly-averaged
daily values here and circular-averaged later in spot_insights.py — a plain
arithmetic mean of e.g. 350° and 10° would wrongly give 180° instead of 0°.

Uses the 2022-2024 window for every spot (same reasoning as
fetch_water_temp.py: independent fetch, not mixed into each spot's own
wave/wind climatology window).

Run once with: .venv/bin/python fetch_directions.py
"""

from pathlib import Path

import numpy as np
import pandas as pd
import requests

from spots import SPOTS

CSV_DIR = Path(__file__).resolve().parent.parent / "CSV"
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


def _circular_daily_mean(times: list[str], degrees: list[float]) -> pd.DataFrame:
    df = pd.DataFrame({"ds": pd.to_datetime(times), "deg": degrees})
    df["date"] = df["ds"].dt.date
    radians = np.deg2rad(df["deg"])
    df["sin"] = np.sin(radians)
    df["cos"] = np.cos(radians)
    daily = df.groupby("date")[["sin", "cos"]].mean()
    daily["y"] = (np.degrees(np.arctan2(daily["sin"], daily["cos"])) + 360) % 360
    daily = daily.reset_index().rename(columns={"date": "ds"})
    daily["ds"] = pd.to_datetime(daily["ds"])
    return daily[["ds", "y"]]


def fetch_wind_direction(lat: float, lon: float) -> pd.DataFrame:
    resp = requests.get(
        ARCHIVE_URL,
        params={"latitude": lat, "longitude": lon, "hourly": "wind_direction_10m",
                "start_date": START_DATE, "end_date": END_DATE},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()["hourly"]
    return _circular_daily_mean(data["time"], data["wind_direction_10m"])


def fetch_swell_direction(lat: float, lon: float) -> pd.DataFrame:
    resp = requests.get(
        MARINE_URL,
        params={"latitude": lat, "longitude": lon, "hourly": "swell_wave_direction",
                "start_date": START_DATE, "end_date": END_DATE},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()["hourly"]
    return _circular_daily_mean(data["time"], data["swell_wave_direction"])


if __name__ == "__main__":
    for spot in SPOTS:
        print(f"Fetching directions for {spot.name}...")
        slug = spot.wave_csv.removesuffix("_wave.csv")
        fetch_wind_direction(spot.lat, spot.lon).to_csv(CSV_DIR / f"{slug}_winddir.csv", index=False)
        fetch_swell_direction(spot.lat, spot.lon).to_csv(CSV_DIR / f"{slug}_swelldir.csv", index=False)
    print("Done.")
