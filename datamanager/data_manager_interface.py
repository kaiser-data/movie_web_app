"""Common interface for any data‑layer implementation.

This abstract base class defines the contract that **all** persistence layers
(in‑memory, SQLite, Postgres, …) must follow so the Flask views can swap them
without changes.  Each concrete implementation *must* raise ``ValueError``
whenever an entity is not found or a duplicate key is detected, keeping error
semantics consistent across back‑ends.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class DataManagerInterface(ABC):
    """Blueprint for a user / movie data manager.

    ----------------------------------------------------------------------
    Method naming conventions
    ----------------------------------------------------------------------
    * ``get_*``  – Pure reads (no side‑effects).
    * ``add_*``  – Insert new rows; raise on duplicates.
    * ``update_*`` – Partial update of an existing row; raise if missing.
    * ``delete_*`` – Permanent removal; raise if missing.
    """

    # ------------------------------ Reads ------------------------------ #

    @abstractmethod
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Return every user in the data store."""

    @abstractmethod
    def get_user_movies(self, user_id: int) -> List[Dict[str, Any]]:
        """Return all movies linked to *user_id* (empty list if none)."""

    # ----------------------------- Inserts ----------------------------- #

    @abstractmethod
    def add_user(self, user_data: Dict[str, Any]) -> None:
        """Insert a new user; raise ``ValueError`` on duplicate id."""

    @abstractmethod
    def add_movie(self, movie_data: Dict[str, Any]) -> None:
        """Insert a new movie; raise ``ValueError`` on duplicate id."""

    # ----------------------------- Updates ----------------------------- #

    @abstractmethod
    def update_user(self, user_id: int, updated_data: Dict[str, Any]) -> None:
        """Patch an existing user row (partial update)."""

    @abstractmethod
    def update_movie(self, movie_id: str | int, updated_data: Dict[str, Any]) -> None:
        """Patch an existing movie row (partial update)."""

    # ----------------------------- Deletes ----------------------------- #

    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        """Remove a user completely (cascades handled by impl)."""

    @abstractmethod
    def delete_movie(self, movie_id: str | int) -> None:
        """Remove a movie completely (plus any orphan cleanup)."""
