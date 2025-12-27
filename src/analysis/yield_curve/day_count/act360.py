from __future__ import annotations

from datetime import datetime

from .base import DayCount


class ACT360(DayCount):
    def year_fraction(self, start_date: datetime, end_date: datetime) -> float:
        delta = (end_date - start_date).days
        return delta / 360.0


