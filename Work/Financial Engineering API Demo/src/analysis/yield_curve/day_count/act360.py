from datetime import date
from .base import DayCount


class ACT360(DayCount):
    """Actual/360 day count convention."""

    def year_fraction(self, start: date, end: date) -> float:
        days = (end - start).days
        return days / 360.0

