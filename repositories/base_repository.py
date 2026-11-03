"""
repositories/base_repository.py
--------------------------------
Generic CSV-backed repository base class.
All concrete repositories inherit from this class.

Design principle: The storage technology (CSV today, SQL tomorrow) is
completely hidden from the service layer.  Swap this base class for a
SQLAlchemy equivalent and services/analytics need zero changes.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Generic, TypeVar, Optional, Callable
import threading

import pandas as pd

from utils.exceptions import DataStorageError

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    """
    Thread-safe generic CSV repository.

    Subclasses must implement:
      - `_get_columns()`  → list of CSV column headers
      - `_to_dict(obj)`   → convert domain object to dict
      - `_from_dict(row)` → reconstruct domain object from dict row
      - `_get_id(obj)`    → return the primary key value of the object
      - `_id_column`      → name of the primary key CSV column (class attribute)
    """

    _id_column: str = "id"              # Override in concrete repos
    _lock = threading.Lock()            # Shared file-write lock per subclass

    def __init__(self, filepath: Path) -> None:
        self._filepath = filepath
        self._ensure_file()

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    def _get_columns(self) -> list[str]:
        """Return ordered list of CSV column names."""

    @abstractmethod
    def _to_dict(self, obj: T) -> dict:
        """Serialize domain object to a plain dict."""

    @abstractmethod
    def _from_dict(self, row: dict) -> T:
        """Deserialize a CSV row dict to the domain object."""

    @abstractmethod
    def _get_id(self, obj: T) -> str:
        """Return the primary key value of a domain object."""

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_file(self) -> None:
        """Create the CSV file with headers if it does not exist."""
        if not self._filepath.exists():
            df = pd.DataFrame(columns=self._get_columns())
            self._write_df(df)

    def _read_df(self) -> pd.DataFrame:
        """Read the CSV into a DataFrame; return empty df on failure."""
        try:
            df = pd.read_csv(self._filepath, dtype=str)
            # Keep only known columns, fill missing ones
            for col in self._get_columns():
                if col not in df.columns:
                    df[col] = ""
            return df[self._get_columns()]
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=self._get_columns())
        except Exception as exc:
            raise DataStorageError(
                f"Failed to read data from {self._filepath.name}.",
                details=str(exc),
            ) from exc

    def _write_df(self, df: pd.DataFrame) -> None:
        """Persist a DataFrame back to CSV."""
        try:
            df.to_csv(self._filepath, index=False)
        except Exception as exc:
            raise DataStorageError(
                f"Failed to write data to {self._filepath.name}.",
                details=str(exc),
            ) from exc

    # ------------------------------------------------------------------
    # Public CRUD
    # ------------------------------------------------------------------

    def get_all(self) -> list[T]:
        """Return all records as domain objects."""
        df = self._read_df()
        return [self._from_dict(row) for row in df.to_dict(orient="records")]

    def get_by_id(self, record_id: str) -> Optional[T]:
        """Return the record with matching primary key, or None."""
        df = self._read_df()
        mask = df[self._id_column].str.upper() == record_id.strip().upper()
        rows = df[mask]
        if rows.empty:
            return None
        return self._from_dict(rows.iloc[0].to_dict())

    def exists(self, record_id: str) -> bool:
        """Return True if a record with the given ID exists."""
        return self.get_by_id(record_id) is not None

    def save(self, obj: T) -> T:
        """
        Insert or update a record.
        If a record with the same primary key exists, it is replaced.
        """
        with self.__class__._lock:
            df = self._read_df()
            row_dict = self._to_dict(obj)
            record_id = str(self._get_id(obj)).upper()
            mask = df[self._id_column].str.upper() == record_id
            new_row = pd.DataFrame([row_dict])
            if mask.any():
                df = df[~mask]
            df = pd.concat([df, new_row], ignore_index=True)
            self._write_df(df)
        return obj

    def delete(self, record_id: str) -> bool:
        """
        Delete the record with the given primary key.
        Returns True if a record was deleted, False if not found.
        """
        with self.__class__._lock:
            df = self._read_df()
            mask = df[self._id_column].str.upper() == record_id.strip().upper()
            if not mask.any():
                return False
            df = df[~mask]
            self._write_df(df)
        return True

    def count(self) -> int:
        """Return total number of records."""
        return len(self._read_df())

    def filter_by(self, **kwargs) -> list[T]:
        """
        Return all records where column values match the given kwargs.
        Comparison is case-insensitive string matching.
        """
        df = self._read_df()
        for col, value in kwargs.items():
            if col in df.columns:
                df = df[df[col].str.upper() == str(value).upper()]
        return [self._from_dict(row) for row in df.to_dict(orient="records")]

    def search(self, column: str, query: str) -> list[T]:
        """Case-insensitive substring search on a single column."""
        df = self._read_df()
        if column not in df.columns:
            return []
        mask = df[column].str.contains(query, case=False, na=False)
        return [self._from_dict(row) for row in df[mask].to_dict(orient="records")]

    def get_dataframe(self) -> pd.DataFrame:
        """
        Return the raw DataFrame for analytics use.
        Analytics layer reads this; it does not call the CSV directly.
        """
        return self._read_df()
