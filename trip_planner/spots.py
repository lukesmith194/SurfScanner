"""Static metadata for the Europe MVP spot list.

Only spots with historical wave/wind CSVs in ../CSV are included. Adding a
new spot means scraping its history the same way (see ../Notebooks) and
adding an entry here.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Spot:
    name: str
    country: str
    lat: float
    lon: float
    # Estimated average cost per night for accommodation + food, in EUR.
    # Manually assigned from general travel-cost knowledge; replace with
    # real pricing data once accommodation partners are integrated.
    nightly_eur: float
    wave_csv: str
    wind_csv: str
    image: str
    blurb: str
    # Nearest airport with scheduled commercial service, as an IATA code.
    # Used to build Skyscanner search links — see flights.py.
    airport_iata: str
    # "good" = frequent scheduled service from multiple countries (a real
    # leisure/business hub). "limited" = few routes and/or low frequency, so
    # flying there directly is often a worse option than it looks from
    # distance alone — see fallback_hub below and flights.py.
    airport_connectivity: str = "good"
    # Only set when airport_connectivity == "limited": a better-connected
    # airport worth flying into instead, as (hub_name, hub_iata, drive_km,
    # drive_hours) for the onward drive from that hub to the spot.
    fallback_hub: tuple[str, str, float, float] | None = None
    # Real nearby town/place name, for Booking.com's place-name search —
    # several spots (e.g. Supertubos, Ribeira d'Ilhas) are break names, not
    # places Booking.com would recognize. See accommodation.py.
    nearby_town: str = ""
    # One authoritative external source backing the blurb's facts (Wikipedia,
    # WSL, a specialist surf guide) — left blank where a search didn't turn
    # up a source solid enough to point users at.
    learn_more_url: str = ""
    # Compass degrees (0-360, meteorological "from" convention, matching
    # Open-Meteo's wind_direction_10m) of the wind direction that is
    # OFFSHORE at this spot — i.e. blowing from land out to sea. For the 5
    # original spots this is the real value scraped from surf-forecast.com
    # in the original project (e.g. Nazaré's "best wind direction is from
    # the east"); for the rest it's inferred from the coastline's known
    # orientation. Used to classify actual wind readings as
    # offshore/onshore/cross-shore in spot_insights.py.
    offshore_deg: float = 90.0


SPOTS = [
    Spot(
        name="Nazaré",
        country="Portugal",
        lat=39.60643,
        lon=-9.06933,
        nightly_eur=70,
        wave_csv="nazare_wave.csv",
        wind_csv="nazare_wind.csv",
        image="nazare.jpg",
        blurb=(
            "World-famous big-wave beach break — home of the Guinness World Record wave, "
            "an 86-foot ride by Sebastian Steudtner in 2020, with earlier records set here "
            "by Rodrigo Koxa (2017) and Garrett McNamara (2011). The offshore Nazaré Canyon "
            "amplifies incoming swell. Best for advanced/expert surfers when it's on."
        ),
        airport_iata="LIS",
        nearby_town="Nazaré, Portugal",
        learn_more_url="https://en.wikipedia.org/wiki/Praia_do_Norte_(Nazar%C3%A9)",
        offshore_deg=90,
    ),
    Spot(
        name="Mundaka",
        country="Spain (Basque Country)",
        lat=43.40728,
        lon=-2.69631,
        nightly_eur=100,
        wave_csv="mundaka_wave.csv",
        wind_csv="mundaka_wind.csv",
        image="mundaka.jpg",
        blurb=(
            "World-class left-hand river-mouth wave that hosted the ASP/WCT tour's "
            "Billabong Pro Mundaka (1999-2009), drawing names like Kelly Slater and "
            "Andy Irons. Powerful and technical — intermediate to advanced."
        ),
        airport_iata="BIO",
        nearby_town="Mundaka, Spain",
        learn_more_url="https://en.wikipedia.org/wiki/Mundaka_wave",
        offshore_deg=180,
    ),
    Spot(
        name="El Fronton",
        country="Spain (Gran Canaria)",
        lat=28.16583,
        lon=-15.65394,
        nightly_eur=45,
        wave_csv="fronton_wave.csv",
        wind_csv="fronton_wind.csv",
        image="fronton.jpeg",
        blurb=(
            "One of Gran Canaria's heaviest waves — a serious reef break some rate among "
            "the best of its kind in the world, mostly ridden by bodyboarders and expert "
            "surfers. Best around low tide, biggest in winter. Advanced only."
        ),
        airport_iata="LPA",
        nearby_town="Gran Canaria, Spain",
        learn_more_url="https://www.stormrider.surf/break/el-fronton",
        offshore_deg=180,
    ),
    Spot(
        name="Mosca Point",
        country="Spain (Gran Canaria)",
        lat=27.83490,
        lon=-15.41864,
        nightly_eur=45,
        wave_csv="mosca_wave.csv",
        wind_csv="mosca_wind.csv",
        image="mosca.jpg",
        blurb=(
            "Sheltered beach and reef break with consistent surf, best around low tide "
            "and biggest in winter. Good for a range of levels."
        ),
        airport_iata="LPA",
        nearby_town="Gran Canaria, Spain",
        learn_more_url="https://www.surf-forecast.com/breaks/Mosca-Point",
        offshore_deg=0,
    ),
    Spot(
        name="Tauro",
        country="Spain (Gran Canaria)",
        lat=27.79353,
        lon=-15.72853,
        nightly_eur=50,
        wave_csv="tauro_wave.csv",
        wind_csv="tauro_wind.csv",
        image="tauro.jpeg",
        blurb="Secluded slab, usually clean. Heavily localized — not recommended for beginners.",
        airport_iata="LPA",
        nearby_town="Gran Canaria, Spain",
        offshore_deg=90,
    ),
    # Below: spots added via fetch_new_spots.py (Open-Meteo historical marine
    # + weather data, 2022-2024 — see that script for why the date window
    # differs from the five spots above). Photos are CC-licensed Wikimedia
    # Commons images fetched via fetch_new_spot_photos.py — attribution for
    # each lives in image_credits.json and is shown on the Spot info page.
    Spot(
        name="Supertubos",
        country="Portugal",
        lat=39.3558,
        lon=-9.3803,
        nightly_eur=55,
        wave_csv="supertubos_wave.csv",
        wind_csv="supertubos_wind.csv",
        image="supertubos.jpg",
        blurb=(
            "Peniche's world-tour barrel — a heavy, hollow beach break for experienced "
            "surfers, and host of the WSL's MEO Rip Curl Pro Portugal (on tour since 2010). "
            "Known for producing first-time Championship Tour winners; a powerful, "
            "unpredictable wave even by tour standards."
        ),
        airport_iata="LIS",
        nearby_town="Peniche, Portugal",
        learn_more_url="https://en.wikipedia.org/wiki/Supertubos",
        offshore_deg=70,
    ),
    Spot(
        name="Ribeira d'Ilhas",
        country="Portugal",
        lat=38.9700,
        lon=-9.4200,
        nightly_eur=55,
        wave_csv="ericeira_wave.csv",
        wind_csv="ericeira_wind.csv",
        image="ericeira.jpg",
        blurb=(
            "Consistent right-hand point break in Ericeira — Europe's first World Surfing "
            "Reserve (2011), and site of Portugal's first national surf championship (1977) "
            "and the first ASP World Championship (1989). Rights can run up to 200m. "
            "Good for all levels."
        ),
        airport_iata="LIS",
        nearby_town="Ericeira, Portugal",
        learn_more_url="https://www.savethewaves.org/ericeira/",
        offshore_deg=90,
    ),
    Spot(
        name="Zarautz",
        country="Spain (Basque Country)",
        lat=43.2833,
        lon=-2.1667,
        nightly_eur=85,
        wave_csv="zarautz_wave.csv",
        wind_csv="zarautz_wind.csv",
        image="zarautz.jpg",
        blurb=(
            "The longest beach in the Basque Country (2.8km) with several sandy-bottom "
            "breaks — smaller, forgiving waves in summer make it one of Europe's best "
            "learner spots, while autumn/winter swells suit intermediate and advanced "
            "surfers. Hosts the San Miguel Pro each September."
        ),
        airport_iata="EAS",
        airport_connectivity="limited",
        fallback_hub=("Bilbao", "BIO", 65, 0.8),
        nearby_town="Zarautz, Spain",
        learn_more_url="https://tourism.euskadi.eus/en/beaches-reservoirs-rivers/zarautz-beach/webtur00-content/en/",
        offshore_deg=180,
    ),
    Spot(
        name="Rodiles",
        country="Spain (Asturias)",
        lat=43.5167,
        lon=-5.3167,
        nightly_eur=70,
        wave_csv="rodiles_wave.csv",
        wind_csv="rodiles_wind.csv",
        image="rodiles.jpg",
        blurb="Estuary-mouth beach break in Asturias with a reliable right-hander. Intermediate friendly.",
        airport_iata="OVD",
        nearby_town="Villaviciosa, Spain",
        offshore_deg=180,
    ),
    Spot(
        name="El Cotillo",
        country="Spain (Fuerteventura)",
        lat=28.6833,
        lon=-14.0167,
        nightly_eur=45,
        wave_csv="elcotillo_wave.csv",
        wind_csv="elcotillo_wind.csv",
        image="elcotillo.jpg",
        blurb=(
            "Laid-back beach and reef breaks on Fuerteventura's north coast — smaller, "
            "beginner-friendly swells in summer, with bigger, more powerful surf for "
            "intermediate/advanced surfers from October to March."
        ),
        airport_iata="FUE",
        nearby_town="El Cotillo, Spain",
        learn_more_url="https://thesurfatlas.com/surfing-in-canary-islands/el-cotillo-surf/",
        offshore_deg=45,
    ),
    Spot(
        name="Fistral Beach",
        country="UK (Cornwall)",
        lat=50.4167,
        lon=-5.1000,
        nightly_eur=75,
        wave_csv="fistral_wave.csv",
        wind_csv="fistral_wind.csv",
        image="fistral.jpg",
        blurb=(
            "Newquay's signature beach break and the historic home of British surfing "
            "since the 1960s — host to Boardmasters (a WSL Qualifying Series stop) and "
            "the English National Surfing Championships. Good for all levels depending "
            "on the bank."
        ),
        airport_iata="NQY",
        airport_connectivity="limited",
        fallback_hub=("Bristol", "BRS", 150, 2.5),
        nearby_town="Newquay, United Kingdom",
        learn_more_url="https://www.surfline.com/surf-news/newquay-where-british-surfing-was-born-and-never-stopped/1eIoRe7fYDHC3usZeASHFr",
        offshore_deg=90,
    ),
    Spot(
        name="Thurso East",
        country="UK (Scotland)",
        lat=58.5950,
        lon=-3.5200,
        nightly_eur=60,
        wave_csv="thurso_wave.csv",
        wind_csv="thurso_wind.csv",
        image="thurso.jpg",
        blurb=(
            "Powerful, world-class right-hand reef break over a flagstone reef in the far "
            "north of Scotland — hosted the O'Neill Coldwater Classic (2006-2011). "
            "Advanced surfers only; a thick wetsuit, boots, gloves and hood are essential "
            "year-round."
        ),
        airport_iata="WIC",
        airport_connectivity="limited",
        fallback_hub=("Inverness", "INV", 170, 2.5),
        nearby_town="Thurso, United Kingdom",
        learn_more_url="https://en.wikipedia.org/wiki/Thurso_East",
        offshore_deg=180,
    ),
    Spot(
        name="Bundoran",
        country="Ireland",
        lat=54.4780,
        lon=-8.2830,
        nightly_eur=65,
        wave_csv="bundoran_wave.csv",
        wind_csv="bundoran_wind.csv",
        image="bundoran.jpg",
        blurb=(
            "Ireland's surf capital — a mix of beach and reef breaks including the famous "
            "Peak. Works year-round but most consistent November-March with a northwest "
            "swell and southeast offshore wind. Suits most levels."
        ),
        airport_iata="NOC",
        airport_connectivity="limited",
        fallback_hub=("Dublin", "DUB", 230, 3.0),
        nearby_town="Bundoran, Ireland",
        learn_more_url="https://surfholidays.com/blog/legendary-surf-spot-the-peak-bundoran/",
        offshore_deg=90,
    ),
    Spot(
        name="Lahinch",
        country="Ireland",
        lat=52.9330,
        lon=-9.3450,
        nightly_eur=65,
        wave_csv="lahinch_wave.csv",
        wind_csv="lahinch_wind.csv",
        image="lahinch.jpg",
        blurb=(
            "Consistent beach break in County Clare, right by the Cliffs of Moher — at "
            "its friendliest in spring through early autumn. Good for beginners through "
            "to advanced."
        ),
        airport_iata="SNN",
        nearby_town="Lahinch, Ireland",
        offshore_deg=90,
    ),
]

# Wave height bands, in feet (matches the units of the scraped data), that
# roughly suit each self-reported level. Used to score a spot's forecast
# average against what the surfer can actually handle/enjoy.
LEVEL_BANDS_FT = {
    "Beginner": (1.0, 4.0),
    "Intermediate": (3.0, 7.0),
    "Advanced": (6.0, 20.0),
}

# Rough short-haul flight cost model used only to estimate total trip cost
# until real flight-search integration exists: a flat base fare plus a
# per-km rate, applied to the great-circle distance from the departure city.
FLIGHT_BASE_EUR = 40.0
FLIGHT_EUR_PER_KM = 0.06

# Departure cities offered in the form, with coordinates used to estimate
# distance (and from it, flight cost) as a proxy until real flight-search
# integration exists.
DEPARTURE_CITIES = {
    "Dublin": (53.3498, -6.2603),
    "London": (51.5074, -0.1278),
    "Paris": (48.8566, 2.3522),
    "Madrid": (40.4168, -3.7038),
    "Lisbon": (38.7223, -9.1393),
    "Amsterdam": (52.3676, 4.9041),
    "Berlin": (52.5200, 13.4050),
    "Barcelona": (41.3851, 2.1734),
    "Rome": (41.9028, 12.4964),
    "Brussels": (50.8503, 4.3517),
    "Frankfurt": (50.1109, 8.6821),
    "Porto": (41.1579, -8.6291),
    "Edinburgh": (55.9533, -3.1883),
    "Copenhagen": (55.6761, 12.5683),
    "Vienna": (48.2082, 16.3738),
}

# IATA airport codes for each departure city, for building Skyscanner search
# links (see flights.py). Where a city is served by several airports,
# Skyscanner's multi-airport city code is used (e.g. "LON" covers Heathrow,
# Gatwick, Stansted, Luton and City) so the search isn't limited to one.
DEPARTURE_AIRPORTS = {
    "Dublin": "DUB",
    "London": "LON",
    "Paris": "PAR",
    "Madrid": "MAD",
    "Lisbon": "LIS",
    "Amsterdam": "AMS",
    "Berlin": "BER",
    "Barcelona": "BCN",
    "Rome": "ROM",
    "Brussels": "BRU",
    "Frankfurt": "FRA",
    "Porto": "OPO",
    "Edinburgh": "EDI",
    "Copenhagen": "CPH",
    "Vienna": "VIE",
}
