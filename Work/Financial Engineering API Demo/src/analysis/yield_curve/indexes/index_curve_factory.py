"""Factory for creating yield curves from index rates"""

from typing import Dict, List, Optional
from ..core.curve_factory import CurveFactory
from ..core.curve import YieldCurve
from .index_bootstrapper import IndexBootstrapper
from .index_registry import IndexRegistry


class IndexCurveFactory:
    """Factory for creating yield curves from interest rate indexes (Murex-style)"""

    @staticmethod
    def create_from_index(
        index_code: str,
        index_rates: List[Dict],
        interpolation: str = "cubic_spline",
        day_count: Optional[str] = None,
        compounding: Optional[str] = None,
    ) -> YieldCurve:
        """Create yield curve from a single index (e.g., SOFR curve)"""
        index_def = IndexRegistry.get(index_code)
        if not index_def:
            raise ValueError(f"Unknown index: {index_code}")
        
        market_data = [{**rate, "index": index_code} for rate in index_rates]
        bootstrapper = IndexBootstrapper()
        tenors, rates = bootstrapper.bootstrap(market_data)
        
        day_count = day_count or index_def.day_count
        compounding = compounding or index_def.compounding
        
        return CurveFactory.create_spot_curve(
            tenors=tenors.tolist(),
            rates=rates.tolist(),
            interpolation=interpolation,
            day_count=day_count,
            compounding=compounding,
        )

    @staticmethod
    def create_from_multiple_indexes(
        index_rates: Dict[str, List[Dict]],
        primary_index: Optional[str] = None,
        interpolation: str = "cubic_spline",
        day_count: str = "ACT/360",
        compounding: str = "simple",
    ) -> YieldCurve:
        """Create yield curve from multiple index sources (Murex-style)"""
        tenors, rates = IndexBootstrapper.create_from_index_rates(
            index_rates=index_rates,
            primary_index=primary_index
        )
        
        if primary_index:
            index_def = IndexRegistry.get(primary_index)
            if index_def:
                day_count = day_count or index_def.day_count
                compounding = compounding or index_def.compounding
        
        return CurveFactory.create_spot_curve(
            tenors=tenors.tolist(),
            rates=rates.tolist(),
            interpolation=interpolation,
            day_count=day_count,
            compounding=compounding,
        )

    @staticmethod
    def list_available_indexes(currency: Optional[str] = None) -> Dict[str, str]:
        """List available indexes, optionally filtered by currency"""
        all_indexes = IndexRegistry.list_all()
        
        if currency:
            currency_upper = currency.upper()
            return {code: index.name for code, index in all_indexes.items() if index.currency.upper() == currency_upper}
        
        return {code: index.name for code, index in all_indexes.items()}

