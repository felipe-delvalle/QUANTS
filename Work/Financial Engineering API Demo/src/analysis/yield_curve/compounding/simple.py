from .base import Compounding


class SimpleCompounding(Compounding):
    """Simple interest compounding."""

    def discount_factor(self, rate: float, tenor: float) -> float:
        return 1.0 / (1.0 + rate * tenor)

    def forward_rate(self, r1: float, t1: float, r2: float, t2: float) -> float:
        df1 = self.discount_factor(r1, t1)
        df2 = self.discount_factor(r2, t2)
        return (df1 / df2 - 1.0) / (t2 - t1)

