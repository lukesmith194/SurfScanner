"""One-off pull of real sea surface temperature for all 14 spots, from the
same Open-Meteo Marine API already used for wave height (see
fetch_new_spots.py for why this API and not scraping a surf-forecast site).

Sea surface temperature has the same ~2022+ coverage limit we found for wave
height, so this uses the 2022-2024 window for every spot regardless of which
window that spot's own wave/wind CSVs use — it's a separate, independent
fetch, only used to derive water temp / wetsuit guidance, not mixed into the
wave/wind climatology.

Run once with: .venv/bin/python fetch_water_temp.py
"""

from pathlib import Path

import pandas as pd
import requests

from spots import SPOTS

CSV_DIR = Path(__file__).resolve().parent.parent / "CSV"
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"
MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"


def fetch_spot(lat: float, lon: float) -> pd.DataFrame:
    resp = requests.get(
        MARINE_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "hourly": "sea_surface_temperature",
            "start_date": START_DATE,
            "end_date": END_DATE,
        },
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()["hourly"]
    df = pd.DataFrame({"ds": pd.to_datetime(data["time"]), "y": data["sea_surface_temperature"]})
    daily = df.groupby(df["ds"].dt.date)["y"].mean().reset_index()
    daily["ds"] = pd.to_datetime(daily["ds"])
    return daily


if __name__ == "__main__":
    for spot in SPOTS:
        print(f"Fetching water temp for {spot.name}...")
        slug = spot.wave_csv.removesuffix("_wave.csv")
        daily = fetch_spot(spot.lat, spot.lon)
        daily.to_csv(CSV_DIR / f"{slug}_watertemp.csv", index=False)
    print("Done.")
