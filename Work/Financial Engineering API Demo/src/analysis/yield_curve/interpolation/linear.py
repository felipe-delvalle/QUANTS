from __future__ import annotations

import numpy as np

from .base import Interpolator


class LinearInterpolator(Interpolator):
    def interpolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        return float(np.interp(target_tenor, tenors, rates))

    def extrapolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        if target_tenor < tenors[0]:
            return float(rates[0])
        return float(rates[-1])


