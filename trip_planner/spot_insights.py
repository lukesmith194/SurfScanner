"""Derived, data-backed insights for the Spot info and Historical pages:
water temperature / wetsuit guidance, and "best months by level" — computed
from the same wave/wind/water-temp CSVs the rest of the app uses, rather
than researched/asserted claims we can't verify per spot.
"""

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from recommender import date_range_month_days, load_series
from spots import LEVEL_BANDS_FT, SPOTS, Spot

CSV_DIR = Path(__file__).resolve().parent.parent / "CSV"

COMPASS_POINTS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]

# Below this wind speed, direction barely matters in practice — call it glassy
# regardless of which way it's blowing.
GLASSY_WIND_KMH = 8.0
MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]

# Standard cold-water surfing wetsuit guidance (widely used rule of thumb
# across wetsuit brands/surf shops) keyed by water temp in °C.
WETSUIT_GUIDE = [
    (24.0, "Boardshorts / swimsuit, rash vest optional"),
    (21.0, "2mm shorty or spring suit"),
    (18.0, "3/2mm full suit"),
    (15.0, "4/3mm full suit + boots"),
    (12.0, "5/4mm full suit, boots, gloves"),
    (float("-inf"), "6/5mm full suit + hood, boots, gloves"),
]


def wetsuit_for_temp(temp_c: float) -> str:
    for threshold, suit in WETSUIT_GUIDE:
        if temp_c >= threshold:
            return suit
    return WETSUIT_GUIDE[-1][1]


def monthly_water_temp(spot: Spot) -> pd.Series:
    """Average water temp (°C) by month (1-12)."""
    slug = spot.wave_csv.removesuffix("_wave.csv")
    df = pd.read_csv(CSV_DIR / f"{slug}_watertemp.csv", parse_dates=["ds"])
    df["month"] = df["ds"].dt.month
    return df.groupby("month")["y"].mean()


def monthly_wave_height(spot: Spot) -> pd.Series:
    """Average wave height (ft) by month (1-12)."""
    df = pd.read_csv(CSV_DIR / spot.wave_csv, parse_dates=["ds"])
    df["month"] = df["ds"].dt.month
    return df.groupby("month")["y"].mean()


@dataclass
class BestMonths:
    level: str
    months: list[str]  # month name abbreviations, in calendar order


def best_months_by_level(spot: Spot) -> list[BestMonths]:
    """For each level, which months' average wave height falls inside that
    level's ideal band (spots.LEVEL_BANDS_FT) — i.e. genuinely data-driven,
    not a general claim about the spot.
    """
    monthly_wave = monthly_wave_height(spot)
    results = []
    for level, (low, high) in LEVEL_BANDS_FT.items():
        months = [
            MONTH_NAMES[month - 1]
            for month in range(1, 13)
            if month in monthly_wave.index and low <= monthly_wave[month] <= high
        ]
        results.append(BestMonths(level=level, months=months))
    return results


def current_conditions_summary(spot: Spot, month: int) -> tuple[float, str]:
    """(water_temp_c, wetsuit_recommendation) for a given calendar month."""
    temps = monthly_water_temp(spot)
    temp_c = float(temps.get(month, temps.mean()))
    return temp_c, wetsuit_for_temp(temp_c)


def all_spots_monthly_wave_table() -> pd.DataFrame:
    """Rows = spot name, columns = month abbreviation, values = avg wave ft.
    Used for the Historical page's heatmap.
    """
    rows = {}
    for spot in SPOTS:
        monthly = monthly_wave_height(spot)
        rows[spot.name] = [monthly.get(m, float("nan")) for m in range(1, 13)]
    return pd.DataFrame.from_dict(rows, orient="index", columns=MONTH_NAMES)


def all_spots_monthly_wind_table() -> pd.DataFrame:
    rows = {}
    for spot in SPOTS:
        df = pd.read_csv(CSV_DIR / spot.wind_csv, parse_dates=["ds"])
        df["month"] = df["ds"].dt.month
        monthly = df.groupby("month")["y"].mean()
        rows[spot.name] = [monthly.get(m, float("nan")) for m in range(1, 13)]
    return pd.DataFrame.from_dict(rows, orient="index", columns=MONTH_NAMES)


def compass_label(deg: float) -> str:
    idx = round(deg / 45) % 8
    return COMPASS_POINTS[idx]


def circular_mean_deg(degrees: pd.Series) -> float:
    radians = np.deg2rad(degrees)
    mean_angle = np.degrees(np.arctan2(np.sin(radians).mean(), np.cos(radians).mean()))
    return float(mean_angle % 360)


def _direction_csv_slug(spot: Spot) -> str:
    return spot.wave_csv.removesuffix("_wave.csv")


def wind_direction_for_range(spot: Spot, start_date: date, end_date: date) -> float:
    """Circular-mean wind direction (°, meteorological 'from' convention)
    for the given trip window, using the same climatology approach as the
    rest of the app (average of matching calendar days across history).
    """
    slug = _direction_csv_slug(spot)
    df = load_series(f"{slug}_winddir.csv")
    month_days = set(date_range_month_days(start_date, end_date))
    hist = df[df["month_day"].isin(month_days)]
    return circular_mean_deg(hist["y"])


def swell_direction_for_range(spot: Spot, start_date: date, end_date: date) -> float:
    slug = _direction_csv_slug(spot)
    df = load_series(f"{slug}_swelldir.csv")
    month_days = set(date_range_month_days(start_date, end_date))
    hist = df[df["month_day"].isin(month_days)]
    return circular_mean_deg(hist["y"])


# (max angular difference from offshore_deg, label, color) — checked in
# order, first match wins. Matches the terminology surf forecast sites use:
# a cross-shore wind is further split into "leans offshore" / "leans onshore"
# depending on which side of the offshore axis it falls on.
WIND_TYPE_BANDS = [
    (45, "Offshore", "green"),
    (90, "Cross-offshore", "blue"),
    (135, "Cross-onshore", "orange"),
    (180, "Onshore", "red"),
]


def classify_wind(wind_deg: float, wind_speed_kmh: float, offshore_deg: float) -> tuple[str, str]:
    """(label, color) from a wind reading and the spot's known offshore
    direction (spots.Spot.offshore_deg). color is one of Streamlit's alert
    colors (green/blue/orange/red), for a consistent visual code.
    """
    if wind_speed_kmh < GLASSY_WIND_KMH:
        return "Glassy", "blue"
    angular_diff = abs(wind_deg - offshore_deg) % 360
    angular_diff = min(angular_diff, 360 - angular_diff)
    for max_diff, label, color in WIND_TYPE_BANDS:
        if angular_diff <= max_diff:
            return label, color
    return "Onshore", "red"
