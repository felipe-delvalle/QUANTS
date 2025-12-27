import numpy as np
from scipy.interpolate import CubicSpline
from .base import Interpolator


class CubicSplineInterpolator(Interpolator):
    """Cubic spline interpolation for smooth curves."""

    def interpolate(self, x: np.ndarray, y: np.ndarray, target: float) -> float:
        if len(x) < 2:
            return float(y[0]) if len(y) > 0 else 0.0
        cs = CubicSpline(x, y, bc_type='natural')
        return float(cs(target))

    def extrapolate(self, x: np.ndarray, y: np.ndarray, target: float) -> float:
        if len(x) < 2:
            return float(y[0]) if len(y) > 0 else 0.0
        cs = CubicSpline(x, y, bc_type='natural')
        return float(cs(target))

