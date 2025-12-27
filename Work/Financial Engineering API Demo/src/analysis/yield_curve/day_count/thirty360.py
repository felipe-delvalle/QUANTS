from datetime import date
from .base import DayCount


class Thirty360(DayCount):
    """30/360 day count convention."""

    def year_fraction(self, start: date, end: date) -> float:
        d1 = min(start.day, 30)
        d2 = min(end.day, 30) if d1 == 30 else end.day
        days = 360 * (end.year - start.year) + 30 * (end.month - start.month) + (d2 - d1)
        return days / 360.0

