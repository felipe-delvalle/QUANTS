from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime


class DayCount(ABC):
    """Base interface for day count conventions."""

    @abstractmethod
    def year_fraction(self, start_date: datetime, end_date: datetime) -> float:
        """Calculate year fraction between dates."""


