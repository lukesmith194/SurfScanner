"""One-off download of freely-licensed photos for the 9 new spots.

Source: Wikimedia Commons, via the Wikipedia/Commons API (not scraping a
rendered page — this is the documented MediaWiki API). Every file on Commons
carries an explicit free license (CC-BY, CC-BY-SA, or public domain), so
unlike Surfline/Getty-style stock photos there's no licensing risk — we just
need to keep the attribution, which this script records into
image_credits.json for the app to display.

Run once with: .venv/bin/python fetch_new_spot_photos.py
"""

import json
import time
from pathlib import Path

import requests

IMAGES_DIR = Path(__file__).resolve().parent.parent / "images"
HEADERS = {"User-Agent": "SurfScannerMVP/1.0 (personal hobby project)"}

# (slug, destination filename, exact Commons "File:" title to fetch)
PHOTOS = [
    ("supertubos", "supertubos.jpg", "File:Peniche Portugal February 2015 16.jpg"),
    ("ericeira", "ericeira.jpg", "File:Ericeira Surf Point 4.jpg"),
    ("zarautz", "zarautz.jpg", "File:Zarautz Vue Camping.jpg"),
    ("rodiles", "rodiles.jpg", "File:Playa de Rodiles.jpg"),
    ("elcotillo", "elcotillo.jpg", "File:Luftbild El Cotillo mit Castillo de El Toston, Westküste - 51499994362.jpg"),
    ("fistral", "fistral.jpg", "File:Fistral Beach.jpg"),
    ("thurso", "thurso.jpg", "File:Thurso from the hill at Mountpleasant - geograph.org.uk - 8869.jpg"),
    ("bundoran", "bundoran.jpg", "File:Bundoranbay.JPG"),
    ("lahinch", "lahinch.jpg", "File:Lahinch.jpg"),
]


def fetch_imageinfo(file_title: str) -> dict:
    resp = requests.get(
        "https://commons.wikimedia.org/w/api.php",
        params={
            "action": "query",
            "titles": file_title,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata",
            "iiurlwidth": 1200,
            "format": "json",
        },
        headers=HEADERS,
        timeout=30,
    )
    resp.raise_for_status()
    pages = resp.json()["query"]["pages"]
    page = next(iter(pages.values()))
    return page["imageinfo"][0]


def download(url: str, dest: Path) -> None:
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    dest.write_bytes(resp.content)


if __name__ == "__main__":
    credits = {}
    for slug, filename, file_title in PHOTOS:
        print(f"Fetching {file_title}...")
        time.sleep(1.5)
        info = fetch_imageinfo(file_title)
        download(info["thumburl"], IMAGES_DIR / filename)

        meta = info.get("extmetadata", {})
        artist = meta.get("Artist", {}).get("value", "Unknown")
        license_name = meta.get("LicenseShortName", {}).get("value", "Unknown license")
        credits[slug] = {
            "artist": artist,
            "license": license_name,
            "source": info.get("descriptionurl", ""),
        }

    credits_path = Path(__file__).resolve().parent / "image_credits.json"
    credits_path.write_text(json.dumps(credits, indent=2))
    print(f"Done. Saved {len(PHOTOS)} photos to {IMAGES_DIR} and credits to {credits_path}")
