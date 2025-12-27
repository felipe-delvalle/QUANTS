from datetime import date
from .base import DayCount


class ACT365(DayCount):
    """Actual/365 day count convention."""

    def year_fraction(self, start: date, end: date) -> float:
        days = (end - start).days
        return days / 365.0

