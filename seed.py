"""
seed.py
--------
Populate the SQLite database with a deterministic demo dataset:

• 5 demo users
• 25 distinct movies (5 per user)
• Poster URLs fetched live from OMDb

Run:
    $ python seed.py
Make sure your .env contains a valid OMDB_API_KEY.

The script is idempotent: it drops and recreates all tables every run.
"""

from __future__ import annotations

import os
import logging
from typing import Dict, List

import requests
from dotenv import load_dotenv

from datamanager.models import db
from datamanager.sqlite_data_manager import SQLiteDataManager
from app import app, data_manager  # re-use the live manager configured in app.py

# --------------------------------------------------------------------------- #
#  Basic configuration                                                        #
# --------------------------------------------------------------------------- #

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)

OMDB_API_KEY = os.getenv("OMDB_API_KEY")
if not OMDB_API_KEY:
    raise SystemExit("❌  OMDB_API_KEY not set in environment – aborting seed.")

# Helper -------------------------------------------------------------------- #


def _fetch_poster(title: str) -> str:
    """Return a poster URL for *title* via OMDb (empty string on failure)."""
    try:
        resp = requests.get(
            "http://www.omdbapi.com/",
            params={"t": title, "apikey": OMDB_API_KEY},
            timeout=10,
        )
        data = resp.json()
        return data.get("Poster", "") if data.get("Response") == "True" else ""
    except Exception as exc:  # noqa: BLE001
        log.warning("Failed to fetch poster for %s – %s", title, exc)
        return ""


# --------------------------------------------------------------------------- #
#  Seed data                                                                  #
# --------------------------------------------------------------------------- #

USER_NAMES: List[str] = ["Alice", "Bob", "Charlie", "Diana", "Eve"]

# 5 distinct movies per user (25 total, unique IMDb IDs)
USER_MOVIES: Dict[int, List[Dict[str, str | int | float]]] = {
    1: [
        {"id": "tt0110912", "name": "Pulp Fiction"},
        {"id": "tt0109830", "name": "Forrest Gump"},
        {"id": "tt0120737", "name": "The Lord of the Rings: The Fellowship of the Ring"},
        {"id": "tt0112573", "name": "Braveheart"},
        {"id": "tt0120815", "name": "Saving Private Ryan"},
    ],
    2: [
        {"id": "tt0137523", "name": "Fight Club"},
        {"id": "tt0167261", "name": "The Lord of the Rings: The Two Towers"},
        {"id": "tt0120689", "name": "The Green Mile"},
        {"id": "tt0102926", "name": "The Silence of the Lambs"},
        {"id": "tt0133093", "name": "The Matrix"},
    ],
    3: [
        {"id": "tt0167260", "name": "The Lord of the Rings: The Return of the King"},
        {"id": "tt0108052", "name": "Schindler's List"},
        {"id": "tt0172495", "name": "Gladiator"},
        {"id": "tt0080684", "name": "Star Wars: Episode V – The Empire Strikes Back"},
        {"id": "tt0816692", "name": "Interstellar"},
    ],
    4: [
        {"id": "tt0468569", "name": "The Dark Knight"},
        {"id": "tt0071562", "name": "The Godfather: Part II"},
        {"id": "tt0317248", "name": "City of God"},
        {"id": "tt0114369", "name": "Se7en"},
        {"id": "tt0103064", "name": "Terminator 2: Judgment Day"},
    ],
    5: [
        {"id": "tt0068646", "name": "The Godfather"},
        {"id": "tt6751668", "name": "Parasite"},
        {"id": "tt7991608", "name": "Jojo Rabbit"},
        {"id": "tt0050083", "name": "12 Angry Men"},
        {"id": "tt8579674", "name": "1917"},
    ],
}


def _populate() -> None:
    """Drop & recreate all tables, seed users and movies, link favorites."""
    with app.app_context():
        log.info("Resetting database …")
        db.drop_all()
        db.create_all()

        # ------------------------------------------------------------------ #
        #  Insert users                                                      #
        # ------------------------------------------------------------------ #
        for idx, name in enumerate(USER_NAMES, start=1):
            data_manager.add_user({"id": idx, "name": name})
        log.info("Inserted %d users.", len(USER_NAMES))

        # ------------------------------------------------------------------ #
        #  Insert movies + link to users                                     #
        # ------------------------------------------------------------------ #
        total_movies = 0
        for user_id, movies in USER_MOVIES.items():
            for m in movies:
                # Fetch poster once per movie
                poster_url = _fetch_poster(m["name"])
                movie_payload = {
                    "id": m["id"],
                    "name": m["name"],
                    "director": "N/A",  # could call OMDb again, but not required
                    "year": 0,
                    "rating": 0.0,
                    "genre": "N/A",
                    "poster": poster_url,
                }
                # Insert (idempotent; skips if already present)
                data_manager.add_movie(movie_payload)
                # Link to user
                data_manager.add_favorite_movie(user_id, m["id"])
                total_movies += 1

        log.info("Inserted %d movies and linked favourites.", total_movies)
        log.info("✅ Database seeded successfully!")


if __name__ == "__main__":
    _populate()
