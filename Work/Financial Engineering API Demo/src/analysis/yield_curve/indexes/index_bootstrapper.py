"""Index-based bootstrapper for yield curve construction"""

from typing import Dict, List, Tuple, Optional
import numpy as np
from ..bootstrapping.base import Bootstrapper
from .index_registry import IndexRegistry


class IndexBootstrapper(Bootstrapper):
    """Bootstrap a yield curve from index rates (SOFR, LIBOR, EURIBOR, etc.)"""

    def bootstrap(self, market_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        if not market_data:
            raise ValueError("No index data provided for bootstrapping")

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
            
            normalized_data.append({"index": index_code, "tenor": tenor, "rate": rate})

        normalized_data.sort(key=lambda x: x["tenor"])
        tenors = np.array([d["tenor"] for d in normalized_data], dtype=float)
        rates = np.array([d["rate"] for d in normalized_data], dtype=float)

        return tenors, rates

    @staticmethod
    def create_from_index_rates(
        index_rates: Dict[str, List[Dict]],
        primary_index: Optional[str] = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Create curve from multiple index sources (Murex-style)"""
        all_data = []
        for index_code, rates in index_rates.items():
            for rate_data in rates:
                rate_data["index"] = index_code
                all_data.append(rate_data)
        
        if primary_index:
            primary_upper = primary_index.upper()
            all_data.sort(key=lambda x: (
                0 if x.get("index", "").upper() == primary_upper else 1,
                x.get("tenor", x.get("maturity", 0))
            ))
        
        bootstrapper = IndexBootstrapper()
        return bootstrapper.bootstrap(all_data)

