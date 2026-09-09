"""Booking.com / Airbnb deep-links for accommodation near a spot.

Same approach as flights.py and Rome2Rio in flights.py — no embedding,
because both sites block it:

- Airbnb sends `X-Frame-Options: SAMEORIGIN` (confirmed via response
  headers), so no browser will render it in our iframe.
- Booking.com currently ships `Content-Security-Policy-Report-Only:
  frame-ancestors 'none'` — report-only for now, but that's a site
  explicitly telegraphing it's about to start blocking framing outright,
  not something worth building on.

What's verified to actually work, checked with real HTTP requests against
airbnb.com/airbnb.ie rather than assumed:

- UPDATE (2026-09): the bounding-box claim below turned out to be stale.
  Airbnb changed behaviour since it was last checked — a bare
  `/s/homes?...&ne_lat=..&ne_lng=..&sw_lat=..&sw_lng=..` request (no place
  name in the path, no `search_type`) now gets an HTTP 301 straight back to
  the plain homepage `/`, silently dropping the entire search including the
  bbox. That's the actual bug the user reported: the generated Airbnb link
  never reached a scoped results page at all.
- The fix verified by real `curl` requests against both www.airbnb.com and
  www.airbnb.ie (this box round-trips through a domain-switch redirect to
  .ie, unrelated to the bug) is to (a) put a non-empty place-name path
  segment in front of `/homes`, e.g. `/s/Nazar%C3%A9--Portugal/homes`, and
  (b) add `search_type=user_map_move`. With both present the request returns
  a real 200 search-results page instead of redirecting, and the bbox is
  what actually drives the results, not the place text: swapping the place
  segment for a deliberately wrong/generic placeholder (`/s/Search--Location/
  homes`) returned the *same* listings — confirmed by grepping the response
  HTML for listing subtitles ("Flat in Nazaré", "Apartment in São Martinho do
  Porto", "Home in Alcobaça"/"Alfeizerão"/"Cela" for the Nazaré box; "Flat in
  Mundaka", "Apartment in Sukarrieta" for the Mundaka box) — all real towns
  inside the requested `ne_lat/ne_lng/sw_lat/sw_lng` box and nowhere else.
  So the place segment only exists to avoid the homepage redirect; the actual
  scoping is still the bbox math below, now confirmed to survive into results
  rather than just "survive the redirect" as previously (wrongly) verified.
  `airbnb_url()` now builds that place segment from `nearby_town`/`name` so
  the URL also reads sensibly, but any non-empty string works.
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
    place_name: str = "Search--Location",
) -> str:
    """Airbnb map search bounded to a real ~radius_km box around (lat, lon).

    `place_name` only fills a path segment Airbnb requires to avoid an
    HTTP 301 redirect back to the plain homepage (dropping the whole
    search) — confirmed by direct HTTP testing that the bbox, not this
    text, is what actually scopes the results (see module docstring).
    Any non-empty string works; pass a real place for a readable URL.
    """
    lat_delta = radius_km / KM_PER_DEGREE_LAT
    lon_delta = radius_km / (KM_PER_DEGREE_LAT * cos(radians(lat)))
    slug = quote((place_name or "Search--Location").replace(", ", "--").replace(" ", "-"))
    return (
        f"https://www.airbnb.com/s/{slug}/homes"
        f"?checkin={checkin.isoformat()}&checkout={checkout.isoformat()}"
        f"&adults={adults}&search_type=user_map_move"
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
            url=airbnb_url(
                spot.lat,
                spot.lon,
                start_date,
                end_date,
                place_name=spot.nearby_town or spot.name,
            ),
            caveat=(
                "Airbnb's own on-page filters (dates, price, etc.) may still "
                "reshuffle or paginate results after the link lands — if the "
                "map view ever looks off, drag/zoom it once to re-trigger "
                f"their search within the ~{ACCOMMODATION_RADIUS_KM:.0f}km box."
            ),
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
