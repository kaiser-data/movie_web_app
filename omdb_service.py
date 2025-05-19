"""Thin service layer for the public **OMDb API**.

The module provides two helpers:

* :func:`fetch_movie_data` – raw HTTP GET by *title*, with basic error guards.
* :func:`extract_movie_data` – normalises the JSON into our ORM‑ready format.

Usage
-----
>>> from omdb_service import fetch_movie_data, extract_movie_data
>>> raw = fetch_movie_data("Inception")
>>> movie = extract_movie_data(raw)
>>> movie["name"], movie["rating"]
('Inception', 8.8)

All network errors, missing API keys and parsing issues are captured and
returned as ``{"Error": "…"}`` so the Flask layer can translate them into
user‑friendly flash messages.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Environment / logging setup
# ---------------------------------------------------------------------------

load_dotenv()  # read .env for OMDB_API_KEY
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_KEY: str | None = os.getenv("OMDB_API_KEY")
OMDB_URL = "http://www.omdbapi.com/"

# ---------------------------------------------------------------------------
# Public helpers
# ---------------------------------------------------------------------------

def fetch_movie_data(title: str) -> Dict[str, Any]:
    """Return *raw* JSON for a given movie **title**.

    Parameters
    ----------
    title : str
        Free‑text title passed straight to OMDb (e.g. "Interstellar").

    Returns
    -------
    dict
        *Successful* – full JSON from OMDb.  
        *Failure* – ``{"Error": "message"}`` with human‑readable reason.
    """
    if not API_KEY:
        logger.error("OMDb API key is missing – set OMDB_API_KEY in .env")
        return {"Error": "OMDb API key not found."}

    url = f"{OMDB_URL}?apikey={API_KEY}&t={title}"
    logger.info("🔍 Requesting OMDb ➜ %s", title)

    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            logger.error("OMDb HTTP %s", resp.status_code)
            return {"Error": f"Request failed with status code {resp.status_code}"}

        payload = resp.json()
        if payload.get("Response") != "True":
            err = payload.get("Error", "Movie not found")
            logger.warning("OMDb error: %s", err)
            return {"Error": err}

        logger.info("✅ OMDb hit – title found")
        return payload
    except Exception as exc:  # pragma: no cover – network edge‑cases
        logger.exception("Exception talking to OMDb: %s", exc)
        return {"Error": str(exc)}


def extract_movie_data(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise *raw* OMDb JSON into our database schema.

    Parameters
    ----------
    raw : dict
        Payload from :func:`fetch_movie_data`.

    Returns
    -------
    dict
        Keys match the SQLAlchemy *Movie* model – ``id``, ``name``, …  
        If *raw* contained an ``Error`` key it is propagated unchanged.
    """
    if "Error" in raw:
        # Propagate failure unchanged so caller can flash the message
        return raw

    try:
        # Safe conversions (default to 0 / 0.0 if parse fails)
        year = int(raw.get("Year", 0)) if raw.get("Year", "0").isdigit() else 0
        rating_str = raw.get("imdbRating", "0")
        rating = float(rating_str) if rating_str.replace(".", "", 1).isdigit() else 0.0

        return {
            "id": raw.get("imdbID", ""),
            "name": raw.get("Title", "N/A"),
            "director": raw.get("Director", "N/A"),
            "year": year,
            "rating": rating,
            "genre": raw.get("Genre", "N/A"),
            "poster": raw.get("Poster", ""),
        }
    except Exception as exc:  # pragma: no cover – defensive
        logger.exception("Error extracting OMDb data: %s", exc)
        return {"Error": str(exc)}


# ---------------------------------------------------------------------------
# Manual test helper – `python omdb_service.py`
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("🎬 OMDb Service Tester – Ctrl+C to quit\n")
    while True:
        try:
            title = input("Enter a movie title: ").strip()
            if not title:
                continue
            raw = fetch_movie_data(title)
            if "Error" in raw:
                print("❌", raw["Error"], "\n")
                continue
            clean = extract_movie_data(raw)
            print("\n✅ Parsed Movie Data:")
            for k, v in clean.items():
                print(f"  {k:<8} : {v}")
            print()
        except KeyboardInterrupt:
            print("\nBye!")
            break
