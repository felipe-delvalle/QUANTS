import numpy as np
from .base import Interpolator


class LogLinearInterpolator(Interpolator):
    """Log-linear interpolation (linear in log space)."""

    def interpolate(self, x: np.ndarray, y: np.ndarray, target: float) -> float:
        log_y = np.log(np.maximum(y, 1e-10))
        log_result = np.interp(target, x, log_y)
        return float(np.exp(log_result))

    def extrapolate(self, x: np.ndarray, y: np.ndarray, target: float) -> float:
        if target < x[0]:
            return float(y[0])
        return float(y[-1])

