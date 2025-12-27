from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np
from scipy.optimize import brentq

from .base import Bootstrapper
from ..compounding.registry import CompoundingRegistry
from ..interpolation.registry import InterpolatorRegistry


class BondBootstrapper(Bootstrapper):
    """
    Bootstrap spot rates from coupon bond prices.
    Expects bonds: [{\"maturity\": float, \"coupon\": float, \"price\": float, \"frequency\": int, \"face_value\": float=100.0}]
    """

    def __init__(self, compounding: str = "simple", interpolation: str = "linear"):
        self.compounding = CompoundingRegistry.get(compounding)
        self.interpolator = InterpolatorRegistry.get(interpolation)

    def bootstrap(self, bonds: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        if not bonds:
            raise ValueError("No bond data provided for bootstrapping")

        bonds_sorted = sorted(bonds, key=lambda b: b["maturity"])
        tenors: List[float] = []
        spot_rates: List[float] = []

        for bond in bonds_sorted:
            maturity = float(bond["maturity"])
            coupon = float(bond.get("coupon", 0.0))
            price = float(bond["price"])
            frequency = int(bond.get("frequency", 2))
            face_value = float(bond.get("face_value", 100.0))

            if maturity <= 0:
                raise ValueError("Bond maturity must be positive")

            # Solve for spot rate that matches the bond price
            rate = self._solve_spot_rate(
                maturity,
                coupon,
                price,
                frequency,
                face_value,
                tenors,
                spot_rates,
            )
            tenors.append(maturity)
            spot_rates.append(rate)

        return np.array(tenors), np.array(spot_rates)

    def _price_with_rate(
        self,
        maturity: float,
        coupon: float,
        price_rate: float,
        frequency: int,
        face_value: float,
        known_tenors: List[float],
        known_rates: List[float],
    ) -> float:
        comp = self.compounding
        total_periods = int(round(maturity * frequency))
        coupon_payment = face_value * coupon / frequency

        # Build tenor grid for cashflows
        times = [(i + 1) / frequency for i in range(total_periods)]
        price = 0.0

        for idx, t in enumerate(times):
            cf = coupon_payment
            if idx == total_periods - 1:
                cf += face_value

            # Determine discount rate for this cashflow
            if t < maturity and known_tenors:
                interp_rate = self.interpolator.interpolate(
                    np.array(known_tenors), np.array(known_rates), t
                )
                df = comp.discount_factor(interp_rate, t)
            else:
                df = comp.discount_factor(price_rate, t)

            price += cf * df

        return price

    def _solve_spot_rate(
        self,
        maturity: float,
        coupon: float,
        market_price: float,
        frequency: int,
        face_value: float,
        known_tenors: List[float],
        known_rates: List[float],
    ) -> float:
        def objective(r: float) -> float:
            return self._price_with_rate(
                maturity, coupon, r, frequency, face_value, known_tenors, known_rates
            ) - market_price

        # Bracket for rates between -5% and 50%
        lower, upper = -0.05, 0.5
        try:
            return float(brentq(objective, lower, upper, maxiter=100))
        except ValueError:
            # Fallback: try a wider bracket
            return float(brentq(objective, -0.1, 1.0, maxiter=200))


