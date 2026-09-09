"""Scoring logic for the Europe MVP trip planner.

Approach: rather than re-running the ARMA/Prophet models from the original
notebooks for a date range that may fall in the future, we use the 2018-2020
scraped history as a climatology — averaging past years' readings for the
same calendar days the trip covers. That's a reasonable proxy for "what's
this spot usually like in that window" without needing a live forecast API.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd

from flights import estimate_travel_cost_eur
from geo import haversine_km
from spots import LEVEL_BANDS_FT, SPOTS, Spot

CSV_DIR = Path(__file__).resolve().parent.parent / "CSV"


@dataclass
class Recommendation:
    spot: Spot
    avg_wave_ft: float
    avg_wind_kmh: float
    distance_km: float
    nights: int
    flight_eur: float
    ground_eur: float
    accommodation_eur: float
    total_cost_eur: float
    level_score: float  # 0-1, how well the average wave height suits the level


def load_series(csv_name: str) -> pd.DataFrame:
    df = pd.read_csv(CSV_DIR / csv_name, parse_dates=["ds"])
    df["month_day"] = df["ds"].dt.strftime("%m-%d")
    return df


def date_range_month_days(start: date, end: date) -> list[str]:
    days = pd.date_range(start, end, freq="D")
    return [d.strftime("%m-%d") for d in days]


def _level_score(avg_wave_ft: float, level: str) -> float:
    """1.0 = smack in the middle of the ideal band, tapering to 0 outside it."""
    low, high = LEVEL_BANDS_FT[level]
    mid = (low + high) / 2
    half_width = (high - low) / 2
    if low <= avg_wave_ft <= high:
        # Closer to the middle of the band scores higher than the edges.
        return 1.0 - 0.3 * (abs(avg_wave_ft - mid) / half_width)
    # Outside the band: decay with distance from the nearest edge.
    edge = low if avg_wave_ft < low else high
    overshoot = abs(avg_wave_ft - edge)
    return max(0.0, 0.7 - 0.15 * overshoot)


def estimate_cost_eur(spot: Spot, distance_km: float, nights: int) -> tuple[float, float, float, float]:
    """(flight, ground travel, accommodation, total) EUR estimate for a trip.

    Delegates the flight-vs-drive decision to estimate_travel_cost_eur so
    this always matches what the "Getting there" section actually recommends
    — see that function's docstring for why that matters.
    """
    flight_eur, ground_eur = estimate_travel_cost_eur(distance_km, spot)
    accommodation_eur = spot.nightly_eur * nights
    return flight_eur, ground_eur, accommodation_eur, flight_eur + ground_eur + accommodation_eur


# Spots costing more than this far over budget are dropped entirely rather
# than just scored down, so the results never show a trip nobody could afford.
MAX_OVER_BUDGET_FRACTION = 0.10


def recommend(
    start_date: date,
    end_date: date,
    level: str,
    departure: tuple[float, float],
    budget_eur: float,
) -> list[Recommendation]:
    """Rank the Europe MVP spots for a trip window, level, origin and budget.

    Sorted by distance from the departure city (closest first), then by
    cheapest estimated total cost; spots more than MAX_OVER_BUDGET_FRACTION
    over budget are excluded outright.
    """
    month_days = set(date_range_month_days(start_date, end_date))
    dep_lat, dep_lon = departure
    nights = max(1, (end_date - start_date).days)

    distances = {
        spot.name: haversine_km(dep_lat, dep_lon, spot.lat, spot.lon) for spot in SPOTS
    }

    results = []
    for spot in SPOTS:
        wave_df = load_series(spot.wave_csv)
        wind_df = load_series(spot.wind_csv)

        wave_hist = wave_df[wave_df["month_day"].isin(month_days)]
        wind_hist = wind_df[wind_df["month_day"].isin(month_days)]
        if wave_hist.empty:
            continue

        avg_wave = float(wave_hist["y"].mean())
        avg_wind = float(wind_hist["y"].mean()) if not wind_hist.empty else float("nan")
        distance_km = distances[spot.name]
        flight_eur, ground_eur, accommodation_eur, total_cost_eur = estimate_cost_eur(
            spot, distance_km, nights
        )

        if total_cost_eur > budget_eur * (1 + MAX_OVER_BUDGET_FRACTION):
            continue

        level_score = _level_score(avg_wave, level)

        results.append(
            Recommendation(
                spot=spot,
                avg_wave_ft=avg_wave,
                avg_wind_kmh=avg_wind,
                distance_km=distance_km,
                nights=nights,
                flight_eur=flight_eur,
                ground_eur=ground_eur,
                accommodation_eur=accommodation_eur,
                total_cost_eur=total_cost_eur,
                level_score=level_score,
            )
        )

    # Closest destination first; cheapest breaks ties (or near-ties) in distance.
    results.sort(key=lambda r: (r.distance_km, r.total_cost_eur))
    return results
