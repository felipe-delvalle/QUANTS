"""
Index-based bootstrapper for yield curve construction
Similar to Murex's index-based curve methodology
"""

from __future__ import annotations

from typing import Dict, List, Tuple, Optional
import numpy as np

from ..bootstrapping.base import Bootstrapper
from .index_registry import IndexRegistry, InterestRateIndex


class IndexBootstrapper(Bootstrapper):
    """
    Bootstrap a yield curve from index rates (SOFR, LIBOR, EURIBOR, etc.)
    Similar to Murex's approach of building curves from multiple index sources.
    
    Expects market_data as list of:
    {
        "index": "SOFR" or "USD-LIBOR-3M", etc.,
        "tenor": years (e.g., 0.25 for 3M),
        "rate": decimal rate (e.g., 0.05 for 5%),
        "date": optional fixing date
    }
    """

    def bootstrap(self, market_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        Bootstrap spot curve from index rates
        
        Args:
            market_data: List of index rate observations
            
        Returns:
            Tuple of (tenors, spot_rates)
        """
        if not market_data:
            raise ValueError("No index data provided for bootstrapping")

        # Validate and normalize index data
        normalized_data = []
        for item in market_data:
            index_code = item.get("index", "").upper()
            index_def = IndexRegistry.get(index_code)
            
            if not index_def:
                raise ValueError(f"Unknown index: {index_code}. Available: {list(IndexRegistry.list_all().keys())}")
            
            tenor = float(item.get("tenor", item.get("maturity", 0)))
            rate = float(item.get("rate", 0))
            
            if tenor <= 0:
                raise ValueError(f"Invalid tenor for index {index_code}: {tenor}")
            
            normalized_data.append({
                "index": index_code,
                "index_def": index_def,
                "tenor": tenor,
                "rate": rate,
            })

        # Sort by tenor
        normalized_data.sort(key=lambda x: x["tenor"])
        
        # Extract tenors and rates
        tenors = np.array([d["tenor"] for d in normalized_data], dtype=float)
        rates = np.array([d["rate"] for d in normalized_data], dtype=float)

        # For now, treat index rates as spot rates
        # In a full implementation, you'd convert index rates to spot rates
        # using bootstrapping from swaps, FRAs, etc.
        
        return tenors, rates

    @staticmethod
    def create_from_index_rates(
        index_rates: Dict[str, List[Dict]],
        primary_index: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create curve from multiple index sources (Murex-style)
        
        Args:
            index_rates: Dict mapping index codes to rate observations
                        e.g., {"SOFR": [{"tenor": 0.25, "rate": 0.05}, ...],
                               "USD-LIBOR-3M": [...]}
            primary_index: Primary index to use if multiple indexes overlap
            
        Returns:
            Tuple of (tenors, spot_rates)
        """
        all_data = []
        
        # Flatten all index rates into single list
        for index_code, rates in index_rates.items():
            for rate_data in rates:
                rate_data["index"] = index_code
                all_data.append(rate_data)
        
        # If primary index specified, prioritize it
        if primary_index:
            primary_upper = primary_index.upper()
            # Sort: primary index first, then others
            all_data.sort(key=lambda x: (
                0 if x.get("index", "").upper() == primary_upper else 1,
                x.get("tenor", x.get("maturity", 0))
            ))
        
        bootstrapper = IndexBootstrapper()
        return bootstrapper.bootstrap(all_data)

