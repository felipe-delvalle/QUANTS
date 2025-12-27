from __future__ import annotations

from datetime import datetime

from .base import DayCount


class Thirty360(DayCount):
    """
    Simplified 30/360 day count convention (US).
    """

    def year_fraction(self, start_date: datetime, end_date: datetime) -> float:
        d1 = start_date.day
        d2 = end_date.day
        m1 = start_date.month
        m2 = end_date.month
        y1 = start_date.year
        y2 = end_date.year

        if d1 == 31:
            d1 = 30
        if d2 == 31 and d1 == 30:
            d2 = 30

        days = 360 * (y2 - y1) + 30 * (m2 - m1) + (d2 - d1)
        return days / 360.0


