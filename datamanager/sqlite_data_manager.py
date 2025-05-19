# datamanager/sqlite_data_manager.py
"""SQLite‑backed implementation of the DataManagerInterface.

This module centralises **all** database operations so the rest of the
application never touches SQLAlchemy sessions directly.  Each public method:

1. Executes inside the **same request‑bound session** (no extra
   ``with app.app_context()`` wrappers), so returned objects remain attached.
2. Provides short, readable docstrings and defensive checks that raise
   ``ValueError`` with clear messages when entities aren’t found.
3. Uses *eager loading* (``selectinload``) sparingly to avoid
   ``DetachedInstanceError`` on relationship access.
"""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from .data_manager_interface import DataManagerInterface
from .models import Movie, User, db


class SQLiteDataManager(DataManagerInterface):
    """High‑level façade for CRUD + relationship ops on **User** / **Movie**.

    Parameters
    ----------
    app : Flask
        The Flask application instance – needed only so we can set the
        SQLAlchemy URI here (keeping config in one place).
    db_uri : str
        A fully‑qualified SQLAlchemy connection string (e.g. ``sqlite:///…``).
    """

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def __init__(self, app, db_uri: str) -> None:
        self.app = app
        app.config.update(
            SQLALCHEMY_DATABASE_URI=db_uri,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
        )

    # ------------------------------------------------------------------
    # User helpers
    # ------------------------------------------------------------------

    def get_all_users(self) -> list[User]:
        """Return *all* users with their ``favorite_movies`` collection loaded."""
        return (
            db.session.query(User)
            .options(selectinload(User.favorite_movies))
            .all()
        )

    def get_user(self, user_id: int) -> User | None:
        """Return a single user (or ``None``) with favorites pre‑loaded."""
        return (
            db.session.query(User)
            .options(selectinload(User.favorite_movies))
            .get(user_id)
        )

    def add_user(self, user_data: dict) -> None:
        """Insert a new ``User`` row.

        Expects ``user_data`` to contain at least ``id`` and ``name`` keys.
        """
        db.session.add(User(id=user_data["id"], name=user_data["name"]))
        db.session.commit()

    def update_user(self, user_id: int, updated_data: dict) -> None:
        """Patch an existing user in‑place."""
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist.")
        user.name = updated_data.get("name", user.name)
        db.session.commit()

    def delete_user(self, user_id: int) -> None:
        """Delete a user *and* cascade/remove any association rows."""
        user = db.session.get(User, user_id)
        if not user:
            raise ValueError(f"User with ID {user_id} does not exist.")
        db.session.delete(user)
        db.session.commit()

    # ------------------------------------------------------------------
    # Movie helpers
    # ------------------------------------------------------------------

    def get_movie(self, movie_id: str) -> Movie | None:
        """Lightweight primary‑key lookup (no relationships)."""
        return db.session.get(Movie, str(movie_id))

    def get_user_movies(self, user_id: int) -> list[Movie]:
        """Return a user’s *current* favourites list (may be empty)."""
        user = self.get_user(user_id)
        return user.favorite_movies if user else []

    def add_movie(self, movie_data: dict) -> bool:
        """Insert a new movie row; return **True** if created, **False** if duplicate."""
        if db.session.get(Movie, str(movie_data["id"])):
            return False  # Existing row – nothing to do

        movie = Movie(
            id=movie_data["id"],
            name=movie_data["name"],
            director=movie_data["director"],
            year=movie_data["year"],
            rating=movie_data["rating"],
            genre=movie_data["genre"],
            poster=movie_data["poster"],
        )
        try:
            db.session.add(movie)
            db.session.commit()
            return True
        except IntegrityError:
            # Rare race‑condition fallback (row inserted by another request)
            db.session.rollback()
            return False

    def update_movie(self, movie_id: str, updated_data: dict) -> None:
        """Update mutable fields on a movie row."""
        movie = db.session.get(Movie, str(movie_id))
        if not movie:
            raise ValueError(f"Movie with ID {movie_id} does not exist.")

        # Only overwrite when a value is provided – otherwise keep current
        movie.name     = updated_data.get("name", movie.name)
        movie.director = updated_data.get("director", movie.director)
        movie.year     = updated_data.get("year", movie.year)
        movie.rating   = updated_data.get("rating", movie.rating)
        movie.genre    = updated_data.get("genre", movie.genre)
        movie.poster   = updated_data.get("poster", movie.poster)
        db.session.commit()

    def delete_movie(self, movie_id: str) -> None:
        """Hard‑delete a movie row (does **not** unlink existing favourites)."""
        movie = db.session.get(Movie, str(movie_id))
        if not movie:
            raise ValueError(f"Movie with ID {movie_id} does not exist.")
        db.session.delete(movie)
        db.session.commit()

    # ------------------------------------------------------------------
    # Linking helpers
    # ------------------------------------------------------------------

    def add_favorite_movie(self, user_id: int, movie_id: str) -> None:
        """Associate an existing movie with a user’s favourites list."""
        user  = db.session.get(User, user_id)
        movie = db.session.get(Movie, str(movie_id))
        if not user or not movie:
            raise ValueError("User or Movie not found.")

        # Relationship collections behave like normal Python lists
        if movie not in user.favorite_movies:
            user.favorite_movies.append(movie)
            db.session.commit()
