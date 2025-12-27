import numpy as np
from .base import Interpolator


class LinearInterpolator(Interpolator):
    """Linear interpolation between points."""

    def interpolate(self, x: np.ndarray, y: np.ndarray, target: float) -> float:
        return float(np.interp(target, x, y))

    def extrapolate(self, x: np.ndarray, y: np.ndarray, target: float) -> float:
        # Linear extrapolation using the nearest two points
        if target < x[0]:
            if len(x) >= 2:
                slope = (y[1] - y[0]) / (x[1] - x[0])
                return float(y[0] + slope * (target - x[0]))
            return float(y[0])
        else:
            if len(x) >= 2:
                slope = (y[-1] - y[-2]) / (x[-1] - x[-2])
                return float(y[-1] + slope * (target - x[-1]))
            return float(y[-1])

