"""Skyscanner deep-links for flight search — deliberately not an embed.

Why not embed Skyscanner in the page: they send `X-Frame-Options: SAMEORIGIN`
on every page (confirmed by checking response headers directly), which tells
every browser to refuse to render their site inside anyone else's iframe.
That's a deliberate anti-clickjacking measure on their end, not something we
can configure around from our side. On top of that, their bot-detection
challenges even a plain read-only request with no browser fingerprint, which
rules out fetching or scraping their results server-side too.

What actually works, and is how most flight metasearch/affiliate links on the
web do this: build a Skyscanner search URL with the origin, destination and
dates baked in, and send the user to it in their own browser tab. Skyscanner
publishes this URL shape for exactly this purpose (origin/destination as
IATA or Skyscanner city codes, dates as YYMMDD):

    https://www.skyscanner.net/transport/flights/{origin}/{destination}/{depart}/{return}/
"""

from dataclasses import dataclass
from datetime import date
from urllib.parse import quote

from geo import haversine_km
from spots import FLIGHT_BASE_EUR, FLIGHT_EUR_PER_KM, Spot

SKYSCANNER_BASE_URL = "https://www.skyscanner.net/transport/flights"
ROME2RIO_BASE_URL = "https://www.rome2rio.com/s"

# Straight-line distance underestimates real road distance (roads aren't
# great circles); this is a rough general-purpose correction factor, not
# routed. Same caveat as the flight-cost estimate elsewhere in this app.
ROAD_DISTANCE_FACTOR = 1.3
AVG_DRIVE_SPEED_KMH = 80.0

# Below this road-distance estimate, driving/train is usually simpler than
# flying (check-in, security, getting to/from two airports) for a leisure
# surf trip — regardless of how well-connected the nearest airport is.
DRIVE_INSTEAD_THRESHOLD_KM = 400.0

# Rough all-in cost of a km of driving/train (fuel or ticket price) — same
# spirit of estimate as FLIGHT_BASE_EUR/FLIGHT_EUR_PER_KM in spots.py.
GROUND_TRAVEL_EUR_PER_KM = 0.15


def estimate_travel_cost_eur(distance_km: float, spot: Spot) -> tuple[float, float]:
    """(flight_eur, ground_eur) for the cheapest realistic way to reach a spot.

    This has to mirror travel_options()'s own decision tree (drive threshold,
    airport connectivity, fallback hub) — the Trip Planner's budget estimate
    was previously computed from a flat flight-cost formula regardless of
    whether a flight was actually the recommended option, which meant a
    drive-recommended trip (e.g. Dublin to Bundoran) was priced as if flown,
    and a fly-to-hub-then-drive trip didn't count the onward drive at all.
    """
    drive_km = distance_km * ROAD_DISTANCE_FACTOR

    if drive_km <= DRIVE_INSTEAD_THRESHOLD_KM:
        return 0.0, drive_km * GROUND_TRAVEL_EUR_PER_KM

    flight_eur = FLIGHT_BASE_EUR + FLIGHT_EUR_PER_KM * distance_km
    ground_eur = 0.0
    if spot.airport_connectivity == "limited" and spot.fallback_hub:
        _, _, hub_drive_km, _ = spot.fallback_hub
        ground_eur = hub_drive_km * GROUND_TRAVEL_EUR_PER_KM
    return flight_eur, ground_eur


def skyscanner_search_url(
    origin_code: str,
    destination_code: str,
    depart_date: date,
    return_date: date,
) -> str:
    depart_str = depart_date.strftime("%y%m%d")
    return_str = return_date.strftime("%y%m%d")
    return (
        f"{SKYSCANNER_BASE_URL}/{origin_code.lower()}/{destination_code.lower()}/"
        f"{depart_str}/{return_str}/"
    )


def rome2rio_url(origin_name: str, destination_name: str) -> str:
    """Multi-modal (train/bus/car rental/drive) comparison for a land leg.

    Rome2Rio publishes this simple two-place-name URL shape for exactly this
    purpose. It's the one link that covers both things asked for — train
    schedules and a rental-car option — for a route we're not treating as a
    flight leg, without us having to reverse-engineer a rail operator's or
    car-rental site's own (undocumented, frequently ID-based) search URLs.
    """
    return f"{ROME2RIO_BASE_URL}/{quote(origin_name)}/{quote(destination_name)}"


@dataclass
class TravelOption:
    mode: str  # "drive" or "fly"
    label: str
    detail: str
    url: str | None  # None for "drive" options
    # Set when this option has a land leg worth comparing train/bus/car-hire
    # for — the direct "drive" option, and the onward leg of a fly-then-drive
    # option. None when the option is a straight flight with no local leg.
    ground_travel_url: str | None = None


def travel_options(
    departure_name: str,
    departure_coords: tuple[float, float],
    origin_iata: str,
    spot: Spot,
    start_date: date,
    end_date: date,
) -> list[TravelOption]:
    """Ranked list of realistic ways to get from the departure city to a spot.

    Distance alone picks a nearest airport that can be a poor choice in
    practice — Bundoran's nearest airport (Knock) has very few scheduled
    routes, so someone flying from Dublin is almost always better off
    driving the ~230km directly, or from further away, flying into Dublin
    itself and driving the rest of the way. This weighs actual airport
    connectivity and straight driving distance, not just proximity.
    """
    dep_lat, dep_lon = departure_coords
    drive_km = haversine_km(dep_lat, dep_lon, spot.lat, spot.lon) * ROAD_DISTANCE_FACTOR
    drive_hours = drive_km / AVG_DRIVE_SPEED_KMH

    options = []

    if drive_km <= DRIVE_INSTEAD_THRESHOLD_KM:
        options.append(
            TravelOption(
                mode="drive",
                label=f"🚗 Drive or take the train from {departure_name}",
                detail=(
                    f"~{drive_km:.0f} km by road (~{drive_hours:.1f} hrs) — often "
                    "simpler than flying for a trip this short."
                ),
                url=None,
                ground_travel_url=rome2rio_url(departure_name, spot.name),
            )
        )

    direct_label = f"✈️ Fly {origin_iata} → {spot.airport_iata}"
    direct_detail = f"Nearest airport to {spot.name}."
    if spot.airport_connectivity == "limited":
        direct_label += " (few scheduled routes — check availability first)"
        direct_detail = f"Nearest airport to {spot.name}, but not well connected."
    options.append(
        TravelOption(
            mode="fly",
            label=direct_label,
            detail=direct_detail,
            url=skyscanner_search_url(origin_iata, spot.airport_iata, start_date, end_date),
        )
    )

    if spot.airport_connectivity == "limited" and spot.fallback_hub:
        hub_name, hub_iata, hub_drive_km, hub_drive_hours = spot.fallback_hub
        # If the recommended hub is the departure city itself, "fly there" is
        # meaningless — the drive-direct option above already covers it.
        if hub_iata == origin_iata:
            return options
        options.append(
            TravelOption(
                mode="fly",
                label=f"✈️ Fly {origin_iata} → {hub_iata} ({hub_name}), then drive",
                detail=(
                    f"Better-connected hub; ~{hub_drive_km:.0f} km "
                    f"(~{hub_drive_hours:.1f} hrs) drive on to {spot.name}."
                ),
                url=skyscanner_search_url(origin_iata, hub_iata, start_date, end_date),
                ground_travel_url=rome2rio_url(hub_name, spot.name),
            )
        )

    return options
