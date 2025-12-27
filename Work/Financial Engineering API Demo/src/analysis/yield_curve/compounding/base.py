from abc import ABC, abstractmethod


class Compounding(ABC):
    """Abstract base class for compounding methods."""

    @abstractmethod
    def discount_factor(self, rate: float, tenor: float) -> float:
        """Calculate discount factor from rate and tenor."""
        pass

    @abstractmethod
    def forward_rate(self, r1: float, t1: float, r2: float, t2: float) -> float:
        """Calculate forward rate between two tenors."""
        pass

