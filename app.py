"""MovieWeb Flask application entry‑point.

This file wires together:

* **Flask** – route definitions and error handlers.
* **SQLAlchemy** – initialisation + table creation.
* **SQLiteDataManager** – high‑level CRUD facade for users/movies.
* **OMDb service helpers** – fetch & normalise movie metadata.

The rest of the project deliberately keeps business logic outside the
presentation layer; routes are therefore thin wrappers that delegate to the
``data_manager``.
"""

from __future__ import annotations

import datetime as _dt
import logging
import os
from typing import Any

from dotenv import load_dotenv
from flask import Flask, flash, redirect, render_template, request, url_for

from datamanager.models import User, db
from datamanager.sqlite_data_manager import SQLiteDataManager
from omdb_service import extract_movie_data, fetch_movie_data

# ---------------------------------------------------------------------------
# Environment & Flask setup
# ---------------------------------------------------------------------------

load_dotenv()  # read .env into os.environ

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev_secret")  # sessions & flashes

# SQLite DB lives in ./data/movies.sqlite
_base_dir = os.path.abspath(os.path.dirname(__file__))
_db_path = os.path.join(_base_dir, "data", "movies.sqlite")
app.config.update(
    SQLALCHEMY_DATABASE_URI=f"sqlite:///{_db_path}",
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Bind SQLAlchemy instance to the app, then create tables if missing
# (idempotent – safe to run every launch)

db.init_app(app)
with app.app_context():
    db.create_all()

# ---------------------------------------------------------------------------
# Data‑manager & helpers
# ---------------------------------------------------------------------------

data_manager = SQLiteDataManager(app, app.config["SQLALCHEMY_DATABASE_URI"])

@app.context_processor
def _inject_year() -> dict[str, Any]:
    """Make ``current_year`` available in **every** Jinja template."""
    return {"current_year": _dt.datetime.now().year}

# ---------------------------------------------------------------------------
# Routes – public pages
# ---------------------------------------------------------------------------

@app.route("/")
def home():
    """Landing page – simple hero + CTA."""
    return render_template("home.html")


@app.route("/users")
def list_users():
    """Render grid of user cards."""
    try:
        users = data_manager.get_all_users()
        return render_template("users.html", users=users)
    except Exception as exc:  # pragma: no cover – generic hard‑fail guard
        flash(f"Error loading users: {exc}", "error")
        return redirect(url_for("home"))


@app.route("/users/<int:user_id>")
def user_movies(user_id: int):
    """Watch‑list page for a single user."""
    user = data_manager.get_user(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("list_users"))

    movies = data_manager.get_user_movies(user_id)
    return render_template("user_movies.html", user=user, movies=movies)


# ---------------------------------------------------------------------------
# Routes – create / update entities
# ---------------------------------------------------------------------------

@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    """Create a new user (auto‑increment id)."""
    if request.method == "POST":
        name = request.form.get("username", "").strip()
        if not name:
            flash("Name cannot be empty!", "error")
            return redirect(url_for("add_user"))

        try:
            max_id: int = db.session.query(db.func.max(User.id)).scalar() or 0
            db.session.add(User(id=max_id + 1, name=name))
            db.session.commit()
            flash("✅ User added successfully!", "success")
            return redirect(url_for("list_users"))
        except Exception as exc:
            db.session.rollback()
            flash(f"❌ Error adding user: {exc}", "error")
            return redirect(url_for("add_user"))

    return render_template("add_user.html")


@app.route("/users/<int:user_id>/add_movie", methods=["GET", "POST"])
def add_movie(user_id: int):
    """Add a movie to *user_id* via OMDb search."""
    user = data_manager.get_user(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("list_users"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Movie title is required!", "error")
            return redirect(url_for("add_movie", user_id=user_id))

        # 1) Fetch & normalise data from OMDb
        raw = fetch_movie_data(title)
        if not raw or "Error" in raw:
            flash(raw.get("Error", "Movie not found."), "error")
            return render_template("add_movie.html", user=user)

        movie_data = extract_movie_data(raw)

        # 2) Insert (idempotent) & link to user
        newly_created = data_manager.add_movie(movie_data)
        try:
            data_manager.add_favorite_movie(user_id, movie_data["id"])
            msg = (
                "✅ Movie added and linked!"
                if newly_created
                else "ℹ️ Movie already existed – linked to your list."
            )
            flash(msg, "success" if newly_created else "info")
        except ValueError:
            flash("⚠️ Movie is already in your favorites.", "error")

        return redirect(url_for("user_movies", user_id=user_id))

    return render_template("add_movie.html", user=user)


@app.route("/users/<int:user_id>/update_movie/<string:movie_id>", methods=["GET", "POST"])
def update_movie(user_id: int, movie_id: str):
    """Edit movie metadata (title, director, etc.)."""
    user = data_manager.get_user(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("list_users"))

    movie = data_manager.get_movie(movie_id)
    if not movie or movie not in user.favorite_movies:
        flash("Movie not found.", "error")
        return redirect(url_for("user_movies", user_id=user_id))

    if request.method == "POST":
        try:
            updated = {
                "name": request.form.get("name") or movie.name,
                "director": request.form.get("director") or movie.director,
                "genre": request.form.get("genre") or movie.genre,
                "year": int(request.form.get("year") or movie.year),
                "rating": float(request.form.get("rating") or movie.rating),
                "poster": request.form.get("poster") or movie.poster,
            }
            data_manager.update_movie(movie_id, updated)
            flash("✅ Movie updated successfully!", "success")
        except Exception as exc:
            flash(f"❌ Error updating movie: {exc}", "error")

        return redirect(url_for("user_movies", user_id=user_id))

    return render_template("update_movie.html", user=user, movie=movie, user_id=user_id)


# ---------------------------------------------------------------------------
# Routes – destructive actions
# ---------------------------------------------------------------------------

@app.route("/users/<int:user_id>/delete_movie/<string:movie_id>")
def delete_movie(user_id: int, movie_id: str):
    """Unlink & delete a movie from the database."""
    try:
        data_manager.delete_movie(movie_id)
        flash("🗑️ Movie deleted successfully!", "success")
    except Exception as exc:
        flash(f"⚠️ Error deleting movie: {exc}", "error")
    return redirect(url_for("user_movies", user_id=user_id))


# ---------------------------------------------------------------------------
# Error handlers
# ---------------------------------------------------------------------------

@app.errorhandler(404)
def page_not_found(_):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(_):
    return render_template("500.html"), 500


# ---------------------------------------------------------------------------
# Main‑entry (development only)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("✅ Running Flask App on http://localhost:5000 …")
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
