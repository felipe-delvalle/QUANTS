from .base import DayCount
from .act365 import ACT365
from .act360 import ACT360
from .thirty360 import Thirty360
from .registry import DayCountRegistry

# Register default day count conventions
DayCountRegistry.register("ACT/365", ACT365)
DayCountRegistry.register("ACT/360", ACT360)
DayCountRegistry.register("30/360", Thirty360)

__all__ = ["DayCount", "ACT365", "ACT360", "Thirty360", "DayCountRegistry"]

