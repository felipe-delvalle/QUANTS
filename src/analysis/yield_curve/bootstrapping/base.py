from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import numpy as np


class Bootstrapper(ABC):
    """Base interface for bootstrapping spot curves from market instruments."""

    @abstractmethod
    def bootstrap(self, market_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Return (tenors, spot_rates)."""


