"""Booking.com / Airbnb deep-links for accommodation near a spot.

Same approach as flights.py and Rome2Rio in flights.py — no embedding,
because both sites block it:

- Airbnb sends `X-Frame-Options: SAMEORIGIN` (confirmed via response
  headers), so no browser will render it in our iframe.
- Booking.com currently ships `Content-Security-Policy-Report-Only:
  frame-ancestors 'none'` — report-only for now, but that's a site
  explicitly telegraphing it's about to start blocking framing outright,
  not something worth building on.

What's verified to actually work, checked with a real (headless) browser
rather than assumed:

- Airbnb's map search takes a bounding box (`ne_lat`/`ne_lng`/`sw_lat`/
  `sw_lng`) plus `checkin`/`checkout`/`adults`, and it survives their
  redirect intact across multiple test coordinates — this gives a genuine,
  precise radius filter, which is how the "10-20km from the spot" requirement
  below is actually enforced for Airbnb.
- Booking.com's standard `ss=` (place name) + `checkin`/`checkout` pattern is
  the documented, widely-used consumer/affiliate URL shape, but in this
  sandboxed environment every request to it hit bot-detection (HTTP 202,
  stripped query params) before reaching real results — the same class of
  block Skyscanner and Rome2Rio showed earlier in this project. That means
  it couldn't be verified server-side the way Airbnb's was. It's still the
  right documented shape to use; just don't assume Booking.com's radius is
  as precisely controlled as Airbnb's — point people at Booking's own
  on-page map/distance filter once they land there.
"""

from dataclasses import dataclass
from datetime import date
from math import cos, radians
from urllib.parse import quote

from spots import Spot

# Midpoint of the "10 to 20 km from the spot" range asked for. Used to build
# Airbnb's bounding box; see ACCOMMODATION_RADIUS_KM usage below.
ACCOMMODATION_RADIUS_KM = 15.0
KM_PER_DEGREE_LAT = 111.0


def airbnb_url(
    lat: float,
    lon: float,
    checkin: date,
    checkout: date,
    radius_km: float = ACCOMMODATION_RADIUS_KM,
    adults: int = 2,
) -> str:
    """Airbnb map search bounded to a real ~radius_km box around (lat, lon)."""
    lat_delta = radius_km / KM_PER_DEGREE_LAT
    lon_delta = radius_km / (KM_PER_DEGREE_LAT * cos(radians(lat)))
    return (
        "https://www.airbnb.com/s/homes"
        f"?checkin={checkin.isoformat()}&checkout={checkout.isoformat()}"
        f"&adults={adults}"
        f"&ne_lat={lat + lat_delta:.4f}&ne_lng={lon + lon_delta:.4f}"
        f"&sw_lat={lat - lat_delta:.4f}&sw_lng={lon - lon_delta:.4f}"
    )


def booking_url(nearby_town: str, checkin: date, checkout: date, adults: int = 2) -> str:
    """Booking.com search centred on the spot's real nearby town."""
    return (
        "https://www.booking.com/searchresults.html"
        f"?ss={quote(nearby_town)}"
        f"&checkin={checkin.isoformat()}&checkout={checkout.isoformat()}"
        f"&group_adults={adults}&no_rooms=1"
    )


@dataclass
class AccommodationOption:
    site: str
    label: str
    url: str
    caveat: str | None = None


def accommodation_options(
    spot: Spot, start_date: date, end_date: date
) -> list[AccommodationOption]:
    return [
        AccommodationOption(
            site="Airbnb",
            label=f"Stays within ~{ACCOMMODATION_RADIUS_KM:.0f} km of {spot.name} on Airbnb ↗",
            url=airbnb_url(spot.lat, spot.lon, start_date, end_date),
        ),
        AccommodationOption(
            site="Booking.com",
            label=f"Stays near {spot.nearby_town} on Booking.com ↗",
            url=booking_url(spot.nearby_town, start_date, end_date),
            caveat=(
                "Booking.com doesn't take an exact radius via link — once "
                "there, use their map/distance filter to stay within "
                f"{ACCOMMODATION_RADIUS_KM:.0f}km or so of the spot."
            ),
        ),
    ]
