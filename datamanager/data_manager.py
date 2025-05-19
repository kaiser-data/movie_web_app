"""In‑memory implementation of :class:`DataManagerInterface`.

This class is **only** for quick unit tests or interactive sessions where you
want a data layer without touching SQLite/SQLAlchemy.  It is *not* used by the
running Flask app (which relies on :class:`SQLiteDataManager`).

The implementation is intentionally simple: two dictionaries backed by Python
lists.  Each method mimics the behaviour (and raises the same errors) as the
real data manager so that higher‑level code can swap the two without changes.
"""

from __future__ import annotations

from data_manager_interface import DataManagerInterface


class InMemoryDataManager(DataManagerInterface):
    """Store *users* and *movies* in plain Python dicts.

    ------------------------------------------------------------------
    Internal structures
    ------------------------------------------------------------------
    ``self.users``
        ``{user_id: {"id": int, "name": str, "favorite_movies": list[int]}}``
    ``self.movies``
        ``{movie_id: {"id": int/str, "name": str, ...}}``
    """

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------

    def __init__(self) -> None:
        # In‑memory stores (never persisted to disk)
        self.users: dict[int, dict] = {}
        self.movies: dict[str | int, dict] = {}

    # ------------------------------------------------------------------
    # Read helpers
    # ------------------------------------------------------------------

    def get_all_users(self) -> list[dict]:
        """Return *all* user dicts (shallow copies)."""
        return list(self.users.values())

    def get_user_movies(self, user_id: int) -> list[dict]:
        """Return every movie favourited by *user_id* (may be empty)."""
        user = self.users.get(user_id)
        if not user:
            return []
        return [self.movies[mid] for mid in user["favorite_movies"] if mid in self.movies]

    # ------------------------------------------------------------------
    # Insert helpers
    # ------------------------------------------------------------------

    def add_user(self, user_data: dict) -> None:
        """Insert a new user; raise if the primary key already exists."""
        user_id = user_data.get("id")
        if user_id in self.users:
            raise ValueError(f"User with ID {user_id} already exists.")
        # Ensure the favorites list exists even if caller forgets
        user_data.setdefault("favorite_movies", [])
        self.users[user_id] = user_data

    def add_movie(self, movie_data: dict) -> None:
        """Insert a new movie; raise if the primary key already exists."""
        movie_id = movie_data.get("id")
        if movie_id in self.movies:
            raise ValueError(f"Movie with ID {movie_id} already exists.")
        self.movies[movie_id] = movie_data

    # ------------------------------------------------------------------
    # Update helpers
    # ------------------------------------------------------------------

    def update_user(self, user_id: int, updated_data: dict) -> None:
        if user_id not in self.users:
            raise ValueError(f"User with ID {user_id} does not exist.")
        self.users[user_id].update(updated_data)

    def update_movie(self, movie_id: str | int, updated_data: dict) -> None:
        if movie_id not in self.movies:
            raise ValueError(f"Movie with ID {movie_id} does not exist.")
        self.movies[movie_id].update(updated_data)

    # ------------------------------------------------------------------
    # Delete helpers
    # ------------------------------------------------------------------

    def delete_user(self, user_id: int) -> None:
        if user_id not in self.users:
            raise ValueError(f"User with ID {user_id} does not exist.")
        del self.users[user_id]

    def delete_movie(self, movie_id: str | int) -> None:
        if movie_id not in self.movies:
            raise ValueError(f"Movie with ID {movie_id} does not exist.")
        del self.movies[movie_id]


# ----------------------------------------------------------------------
# Demonstration block: ``python -m datamanager.in_memory_data_manager``
# ----------------------------------------------------------------------

if __name__ == "__main__":
    manager = InMemoryDataManager()

    # 1) Seed demo data -------------------------------------------------
    manager.add_user({"id": 1, "name": "Alice"})
    manager.add_user({"id": 2, "name": "Bob"})

    manager.add_movie({"id": 101, "name": "Inception", "director": "Christopher Nolan", "year": 2010, "rating": 8.7})
    manager.add_movie({"id": 102, "name": "Interstellar", "director": "Christopher Nolan", "year": 2014, "rating": 8.6})

    # 2) Link favourite --------------------------------------------------
    manager.users[1]["favorite_movies"].append(101)

    # 3) Show output -----------------------------------------------------
    print("All Users:", manager.get_all_users())
    print("Alice's Movies:", manager.get_user_movies(1))

    # 4) Delete & verify -------------------------------------------------
    manager.delete_movie(101)
    print("After deletion:", manager.get_user_movies(1))
