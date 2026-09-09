"""One-off data pull for new European spots, from Open-Meteo.

Why Open-Meteo instead of Surfline / Magic Seaweed / surf-forecast: it's a
free, keyless API (no login, no scraping of a rendered page), it's fine for
this kind of non-commercial personal project, and — unlike Magic Seaweed,
which no longer exists as an independent site — it's an actual live,
documented API. Surfline and surf-forecast.com's terms of service both
prohibit automated scraping of their site data, so we're deliberately not
building a scraper against either.

Wave height comes from the Marine Weather API (ERA5-based significant wave
height, in meters, converted to feet to match the existing CSVs). Wind speed
comes from the general Historical Weather API (10m wind speed, already in
km/h). Both are aggregated to a daily mean, in the same `ds,y` shape as the
existing CSV/*.csv files, over the same 2018-2020 window as the original
scraped data so historical comparisons line up.

Run once with: .venv/bin/python fetch_new_spots.py
"""

from pathlib import Path

import pandas as pd
import requests

CSV_DIR = Path(__file__).resolve().parent.parent / "CSV"
# Open-Meteo's marine wave model archive only goes back to ~2022 (unlike its
# general weather archive, which goes back decades) — confirmed by probing
# the API directly. Use the same 2022-2024 window for wind too so wave and
# wind stay aligned for these spots, even though the older 2018-2020 spots'
# data predates this.
START_DATE = "2022-01-01"
END_DATE = "2024-12-31"
METERS_TO_FEET = 3.28084

MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"

# New European spots to add. Coordinates are the break's approximate
# take-off point / beach. nightly_eur and blurb feed straight into spots.py.
NEW_SPOTS = [
    {
        "slug": "supertubos",
        "name": "Supertubos",
        "country": "Portugal",
        "lat": 39.3558,
        "lon": -9.3803,
        "nightly_eur": 55,
        "blurb": "Peniche's world-tour barrel — a heavy, hollow beach break for experienced surfers.",
    },
    {
        "slug": "ericeira",
        "name": "Ribeira d'Ilhas",
        "country": "Portugal",
        "lat": 38.9700,
        "lon": -9.4200,
        "nightly_eur": 55,
        "blurb": "Consistent right-hand point break in Ericeira, Europe's first World Surfing Reserve. Good for all levels.",
    },
    {
        "slug": "zarautz",
        "name": "Zarautz",
        "country": "Spain (Basque Country)",
        "lat": 43.2833,
        "lon": -2.1667,
        "nightly_eur": 85,
        "blurb": "Long, forgiving beach break in the Basque Country — one of Europe's best learner/intermediate waves.",
    },
    {
        "slug": "rodiles",
        "name": "Rodiles",
        "country": "Spain (Asturias)",
        "lat": 43.5167,
        "lon": -5.3167,
        "nightly_eur": 70,
        "blurb": "Estuary-mouth beach break in Asturias with a reliable right-hander. Intermediate friendly.",
    },
    {
        "slug": "elcotillo",
        "name": "El Cotillo",
        "country": "Spain (Fuerteventura)",
        "lat": 28.6833,
        "lon": -14.0167,
        "nightly_eur": 45,
        "blurb": "Laid-back beach and reef breaks on Fuerteventura's north coast, with options for most levels.",
    },
    {
        "slug": "fistral",
        "name": "Fistral Beach",
        "country": "UK (Cornwall)",
        "lat": 50.4167,
        "lon": -5.1000,
        "nightly_eur": 75,
        "blurb": "Newquay's signature beach break and the UK's competitive surfing hub. Good for all levels depending on the bank.",
    },
    {
        "slug": "thurso",
        "name": "Thurso East",
        "country": "UK (Scotland)",
        "lat": 58.5950,
        "lon": -3.5200,
        "nightly_eur": 60,
        "blurb": "Powerful, world-class right-hand reef break in the far north of Scotland. Advanced surfers, cold water.",
    },
    {
        "slug": "bundoran",
        "name": "Bundoran",
        "country": "Ireland",
        "lat": 54.4780,
        "lon": -8.2830,
        "nightly_eur": 65,
        "blurb": "Ireland's surf capital — a mix of beach and reef breaks including the famous Peak, suiting most levels.",
    },
    {
        "slug": "lahinch",
        "name": "Lahinch",
        "country": "Ireland",
        "lat": 52.9330,
        "lon": -9.3450,
        "nightly_eur": 65,
        "blurb": "Consistent beach break in County Clare, right by the Cliffs of Moher. Good for beginners through to advanced.",
    },
]


def fetch_daily_series(url: str, params: dict, value_key: str) -> pd.DataFrame:
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()["hourly"]
    df = pd.DataFrame({"ds": pd.to_datetime(data["time"]), "y": data[value_key]})
    daily = df.groupby(df["ds"].dt.date)["y"].mean().reset_index()
    daily["ds"] = pd.to_datetime(daily["ds"])
    return daily


def fetch_spot(slug: str, lat: float, lon: float) -> None:
    wave_daily = fetch_daily_series(
        MARINE_URL,
        {"latitude": lat, "longitude": lon, "hourly": "wave_height", "start_date": START_DATE, "end_date": END_DATE},
        "wave_height",
    )
    wave_daily["y"] = wave_daily["y"] * METERS_TO_FEET
    wave_daily.to_csv(CSV_DIR / f"{slug}_wave.csv", index=False)

    wind_daily = fetch_daily_series(
        ARCHIVE_URL,
        {"latitude": lat, "longitude": lon, "hourly": "wind_speed_10m", "start_date": START_DATE, "end_date": END_DATE},
        "wind_speed_10m",
    )
    wind_daily.to_csv(CSV_DIR / f"{slug}_wind.csv", index=False)


if __name__ == "__main__":
    CSV_DIR.mkdir(exist_ok=True)
    for spot in NEW_SPOTS:
        print(f"Fetching {spot['name']}...")
        fetch_spot(spot["slug"], spot["lat"], spot["lon"])
    print(f"Done. Wrote {len(NEW_SPOTS) * 2} CSV files to {CSV_DIR}")
