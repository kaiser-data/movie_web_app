"""SQLAlchemy ORM models for the MovieWeb application.

This module defines two domain entities, **User** and **Movie**, plus the
association table that models a many‑to‑many relationship between them.  It is
intentionally thin – no business logic or helper methods – keeping the ORM
layer focused on persistence only.  All higher‑level operations live in the
Data‑Manager classes.
"""

from __future__ import annotations

from flask_sqlalchemy import SQLAlchemy

# ---------------------------------------------------------------------------
# SQLAlchemy initialisation (bound later inside app.py)
# ---------------------------------------------------------------------------

db = SQLAlchemy()

# ---------------------------------------------------------------------------
# Association table – maps users <-> movies (watch‑list entries)
# ---------------------------------------------------------------------------

user_movie = db.Table(
    "user_movie",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("movie_id", db.String(50), db.ForeignKey("movies.id"), primary_key=True),
)

# ---------------------------------------------------------------------------
# User entity
# ---------------------------------------------------------------------------

class User(db.Model):
    """Application user (profile).

    Attributes
    ----------
    id : int
        Primary key, auto‑increment integer.
    name : str
        Display name (unique constraint handled at app layer).
    favorite_movies : list[Movie]
        Relationship populated via *user_movie* association table.
    """

    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(100), nullable=False)

    # Use default "select" loading so objects remain tied to session
    favorite_movies = db.relationship("Movie", secondary=user_movie, backref="users")

    # ------------------------------------------------------------------
    # Magic / dunder helpers
    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        return f"<User id={self.id} name='{self.name}'>"


# ---------------------------------------------------------------------------
# Movie entity
# ---------------------------------------------------------------------------

class Movie(db.Model):
    """Movie metadata fetched from OMDb.

    Attributes
    ----------
    id : str
        IMDb ID (e.g. ``tt0133093``) – chosen as primary key.
    name : str
        Official title.
    director : str
        Director(s) (comma‑separated if multiple).
    year : int
        Release year.
    rating : float
        IMDb rating (0‑10 scale).
    genre : str | None
        Comma‑separated genre list (may be ``None`` if OMDb lacks data).
    poster : str | None
        URL to the poster artwork.
    """

    __tablename__ = "movies"

    id: str = db.Column(db.String(50), primary_key=True)  # OMDb compatibility
    name: str = db.Column(db.String(200), nullable=False)
    director: str = db.Column(db.String(100), nullable=False)
    year: int = db.Column(db.Integer, nullable=False)
    rating: float = db.Column(db.Float, nullable=False)
    genre: str | None = db.Column(db.String(100))
    poster: str | None = db.Column(db.String(255))

    def __repr__(self) -> str:  # pragma: no cover
        return (
            "<Movie id='{}' name='{}' year={} rating={}>".format(
                self.id, self.name, self.year, self.rating
            )
        )
