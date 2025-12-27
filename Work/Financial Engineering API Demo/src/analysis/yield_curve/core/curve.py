from __future__ import annotations

import numpy as np
from typing import List, Optional, Sequence

from ..interpolation.registry import InterpolatorRegistry
from ..day_count.registry import DayCountRegistry
from ..compounding.registry import CompoundingRegistry
from ..interpolation.base import Interpolator
from ..day_count.base import DayCount
from ..compounding.base import Compounding


class YieldCurve:
    """
    Represents a yield curve with interchangeable interpolation, day count,
    and compounding strategies.
    """

    def __init__(
        self,
        tenors: Sequence[float],
        rates: Sequence[float],
        interpolator: Optional[Interpolator] = None,
        day_count: Optional[DayCount] = None,
        compounding: Optional[Compounding] = None,
        curve_type: str = "spot",
    ):
        if len(tenors) != len(rates):
            raise ValueError("Tenors and rates must have the same length")

        self.tenors = np.array(tenors, dtype=float)
        self.rates = np.array(rates, dtype=float)

        if np.any(self.tenors <= 0):
            raise ValueError("Tenors must be positive")

        sort_idx = np.argsort(self.tenors)
        self.tenors = self.tenors[sort_idx]
        self.rates = self.rates[sort_idx]

        self.interpolator = interpolator or InterpolatorRegistry.get("linear")
        self.day_count = day_count or DayCountRegistry.get("ACT/365")
        self.compounding = compounding or CompoundingRegistry.get("simple")
        self.curve_type = curve_type

    def spot_rate(self, tenor: float) -> float:
        """
        Get spot rate for a given tenor, with interpolation/extrapolation.
        """
        tenor = float(tenor)
        if tenor <= 0:
            raise ValueError("Tenor must be positive")
        match_idx = np.where(np.isclose(self.tenors, tenor))[0]
        if match_idx.size > 0:
            return float(self.rates[match_idx[0]])
        if tenor < self.tenors[0] or tenor > self.tenors[-1]:
            return float(self.interpolator.extrapolate(self.tenors, self.rates, tenor))
        return float(self.interpolator.interpolate(self.tenors, self.rates, tenor))

    def discount_factor(self, tenor: float) -> float:
        """
        Compute discount factor using the configured compounding method.
        """
        rate = self.spot_rate(tenor)
        return float(self.compounding.discount_factor(rate, tenor))

    def forward_rate(self, t1: float, t2: float) -> float:
        """
        Compute forward rate between t1 and t2 using spot rates.
        """
        if t2 <= t1:
            raise ValueError("t2 must be greater than t1")
        r1 = self.spot_rate(t1)
        r2 = self.spot_rate(t2)
        return float(self.compounding.forward_rate(r1, t1, r2, t2))

    def zero_coupon_price(self, tenor: float, face_value: float = 100.0) -> float:
        """
        Price a zero-coupon bond at the given tenor.
        """
        df = self.discount_factor(tenor)
        return float(face_value * df)

    def to_dict(self) -> dict:
        """
        Serialize curve points.
        """
        return {
            "tenors": self.tenors.tolist(),
            "rates": self.rates.tolist(),
            "curve_type": self.curve_type,
        }


