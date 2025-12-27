from __future__ import annotations

import numpy as np

from .base import Interpolator


class LogLinearInterpolator(Interpolator):
    """
    Log-linear interpolation on discount factors implied by simple compounding.
    """

    def interpolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        log_rates = np.log(np.maximum(rates, 1e-8))
        log_interp = np.interp(target_tenor, tenors, log_rates)
        return float(np.exp(log_interp))

    def extrapolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        # Flat extrapolation on rate level
        if target_tenor < tenors[0]:
            return float(rates[0])
        return float(rates[-1])


