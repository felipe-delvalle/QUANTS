"""
Factory for creating yield curves from index rates
Similar to Murex's index-based curve construction
"""

from __future__ import annotations

from typing import Dict, List, Optional

from ..core.curve_factory import CurveFactory
from ..core.curve import YieldCurve
from .index_bootstrapper import IndexBootstrapper
from .index_registry import IndexRegistry


class IndexCurveFactory:
    """
    Factory for creating yield curves from interest rate indexes
    Similar to Murex's index-based curve methodology
    """

    @staticmethod
    def create_from_index(
        index_code: str,
        index_rates: List[Dict],
        interpolation: str = "cubic_spline",
        day_count: Optional[str] = None,
        compounding: Optional[str] = None,
    ) -> YieldCurve:
        """
        Create yield curve from a single index (e.g., SOFR curve)
        
        Args:
            index_code: Index code (e.g., "SOFR", "USD-LIBOR-3M")
            index_rates: List of rate observations for this index
                        [{"tenor": 0.25, "rate": 0.05}, ...]
            interpolation: Interpolation method
            day_count: Day count convention (uses index default if None)
            compounding: Compounding method (uses index default if None)
            
        Returns:
            YieldCurve instance
        """
        index_def = IndexRegistry.get(index_code)
        if not index_def:
            raise ValueError(f"Unknown index: {index_code}")
        
        # Add index code to each rate observation
        market_data = [
            {**rate, "index": index_code}
            for rate in index_rates
        ]
        
        bootstrapper = IndexBootstrapper()
        tenors, rates = bootstrapper.bootstrap(market_data)
        
        # Use index defaults if not specified
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
        """
        Create yield curve from multiple index sources (Murex-style)
        
        This allows combining different indexes to build a comprehensive curve:
        - Short end: OIS rates (SOFR, ESTR, SONIA)
        - Medium term: IBOR rates (LIBOR, EURIBOR)
        - Long end: Swap rates or Treasury rates
        
        Args:
            index_rates: Dict mapping index codes to rate observations
                        {
                            "SOFR": [{"tenor": 0.25, "rate": 0.05}, ...],
                            "USD-LIBOR-3M": [{"tenor": 0.5, "rate": 0.052}, ...],
                            ...
                        }
            primary_index: Primary index to use for defaults (currency, day count, etc.)
            interpolation: Interpolation method
            day_count: Day count convention
            compounding: Compounding method
            
        Returns:
            YieldCurve instance
        """
        tenors, rates = IndexBootstrapper.create_from_index_rates(
            index_rates=index_rates,
            primary_index=primary_index
        )
        
        # If primary index specified, use its defaults
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
        """
        List available indexes, optionally filtered by currency
        
        Args:
            currency: Optional currency filter (USD, EUR, GBP, etc.)
            
        Returns:
            Dict mapping index codes to names
        """
        all_indexes = IndexRegistry.list_all()
        
        if currency:
            currency_upper = currency.upper()
            filtered = {
                code: index.name
                for code, index in all_indexes.items()
                if index.currency.upper() == currency_upper
            }
            return filtered
        
        return {code: index.name for code, index in all_indexes.items()}

