from abc import ABC, abstractmethod
import numpy as np


class Interpolator(ABC):
    """Abstract base class for interpolation strategies."""

    @abstractmethod
    def interpolate(self, x: np.ndarray, y: np.ndarray, target: float) -> float:
        """Interpolate a value at target given known x, y points."""
        pass

    def extrapolate(self, x: np.ndarray, y: np.ndarray, target: float) -> float:
        """Extrapolate beyond the data range. Default: flat extrapolation."""
        if target < x[0]:
            return float(y[0])
        return float(y[-1])

