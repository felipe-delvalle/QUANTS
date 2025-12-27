from __future__ import annotations

from typing import Dict, List

from ..interpolation.registry import InterpolatorRegistry
from ..day_count.registry import DayCountRegistry
from ..compounding.registry import CompoundingRegistry
from ..bootstrapping.registry import BootstrapperRegistry
from .curve import YieldCurve


class CurveFactory:
    """Factory helpers for constructing yield curves with registered strategies."""

    @staticmethod
    def create_spot_curve(
        tenors: List[float],
        rates: List[float],
        interpolation: str = "linear",
        day_count: str = "ACT/365",
        compounding: str = "simple",
    ) -> YieldCurve:
        interpolator = InterpolatorRegistry.get(interpolation)
        day_count_obj = DayCountRegistry.get(day_count)
        compounding_obj = CompoundingRegistry.get(compounding)

        return YieldCurve(
            tenors=tenors,
            rates=rates,
            interpolator=interpolator,
            day_count=day_count_obj,
            compounding=compounding_obj,
            curve_type="spot",
        )

    @staticmethod
    def create_from_bonds(
        bonds: List[Dict],
        bootstrapper_type: str = "bond",
        interpolation: str = "cubic_spline",
        day_count: str = "ACT/365",
        compounding: str = "simple",
    ) -> YieldCurve:
        bootstrapper = BootstrapperRegistry.get(bootstrapper_type)
        tenors, rates = bootstrapper.bootstrap(bonds)
        return CurveFactory.create_spot_curve(
            tenors,
            rates,
            interpolation=interpolation,
            day_count=day_count,
            compounding=compounding,
        )

    @staticmethod
    def create_from_deposits(
        deposits: List[Dict],
        bootstrapper_type: str = "deposit",
        interpolation: str = "linear",
        day_count: str = "ACT/365",
        compounding: str = "simple",
    ) -> YieldCurve:
        bootstrapper = BootstrapperRegistry.get(bootstrapper_type)
        tenors, rates = bootstrapper.bootstrap(deposits)
        return CurveFactory.create_spot_curve(
            tenors,
            rates,
            interpolation=interpolation,
            day_count=day_count,
            compounding=compounding,
        )

