from __future__ import annotations

from abc import ABC, abstractmethod


class Compounding(ABC):
    """Base compounding interface."""

    @abstractmethod
    def discount_factor(self, rate: float, tenor: float) -> float:
        """Calculate discount factor."""

    @abstractmethod
    def forward_rate(self, r1: float, t1: float, r2: float, t2: float) -> float:
        """Calculate forward rate between t1 and t2."""


