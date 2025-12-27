from abc import ABC, abstractmethod
from datetime import date


class DayCount(ABC):
    """Abstract base class for day count conventions."""

    @abstractmethod
    def year_fraction(self, start: date, end: date) -> float:
        """Calculate the year fraction between two dates."""
        pass

