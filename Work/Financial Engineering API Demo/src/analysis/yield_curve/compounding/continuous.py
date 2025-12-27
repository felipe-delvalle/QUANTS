import numpy as np
from .base import Compounding


class ContinuousCompounding(Compounding):
    """Continuous compounding."""

    def discount_factor(self, rate: float, tenor: float) -> float:
        return float(np.exp(-rate * tenor))

    def forward_rate(self, r1: float, t1: float, r2: float, t2: float) -> float:
        return float((r2 * t2 - r1 * t1) / (t2 - t1))

