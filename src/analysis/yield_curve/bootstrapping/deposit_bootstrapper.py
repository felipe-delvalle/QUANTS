from __future__ import annotations

from typing import Dict, List, Tuple
import numpy as np

from .base import Bootstrapper


class DepositBootstrapper(Bootstrapper):
    """
    Bootstrap a spot curve from deposit rates (money market instruments).
    Expects market_data as list of {\"maturity\": years, \"rate\": decimal}.
    """

    def bootstrap(self, market_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        if not market_data:
            raise ValueError("No deposit data provided for bootstrapping")

        deposits = sorted(market_data, key=lambda x: x["maturity"])
        tenors = np.array([float(d["maturity"]) for d in deposits], dtype=float)
        rates = np.array([float(d["rate"]) for d in deposits], dtype=float)

        if (tenors <= 0).any():
            raise ValueError("Deposit maturities must be positive")

        return tenors, rates


