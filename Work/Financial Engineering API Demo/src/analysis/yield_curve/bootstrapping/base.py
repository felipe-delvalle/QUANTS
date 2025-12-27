from abc import ABC, abstractmethod
from typing import Dict, List, Tuple
import numpy as np


class Bootstrapper(ABC):
    """Abstract base class for bootstrapping algorithms."""

    @abstractmethod
    def bootstrap(self, market_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Bootstrap spot rates from market data.
        
        Returns:
            Tuple of (tenors, spot_rates)
        """
        pass

