from __future__ import annotations

from abc import ABC, abstractmethod
import numpy as np


class Interpolator(ABC):
    """Base interface for interpolation/extrapolation strategies."""

    @abstractmethod
    def interpolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        """Interpolate rate for target tenor."""

    @abstractmethod
    def extrapolate(self, tenors: np.ndarray, rates: np.ndarray, target_tenor: float) -> float:
        """Extrapolate rate beyond known curve."""


