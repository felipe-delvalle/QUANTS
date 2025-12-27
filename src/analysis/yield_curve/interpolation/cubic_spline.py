from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline

from .base import Interpolator


class CubicSplineInterpolator(Interpolator):
    def __init__(self):
        self._spline = None
        self._cache_key = None

    def _ensure_spline(self, tenors: np.ndarray, rates: np.ndarray):
        cache_key = (tuple(tenors.tolist()), tuple(rates.tolist()))
        if self._spline is None or self._cache_key != cache_key:
            self._spline = CubicSpline(tenors, rates, bc_type="natural")
            self._cache_key = cache_key

    def interpolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        self._ensure_spline(tenors, rates)
        return float(self._spline(target_tenor))

    def extrapolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        # Use linear extrapolation based on end slopes
        self._ensure_spline(tenors, rates)
        if target_tenor < tenors[0]:
            slope = self._spline(tenors[1], 1)
            return float(rates[0] + slope * (target_tenor - tenors[0]))
        slope = self._spline(tenors[-1], 1)
        return float(rates[-1] + slope * (target_tenor - tenors[-1]))


