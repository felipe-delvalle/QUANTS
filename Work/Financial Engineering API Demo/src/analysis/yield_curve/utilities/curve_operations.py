from __future__ import annotations

from typing import Sequence, Tuple
import numpy as np


def ensure_sorted_unique(tenors: Sequence[float], rates: Sequence[float]) -> Tuple[np.ndarray, np.ndarray]:
    """
    Ensure tenors/rates are sorted by tenor and remove duplicates by keeping first occurrence.
    """
    tenors_arr = np.array(tenors, dtype=float)
    rates_arr = np.array(rates, dtype=float)

    sort_idx = np.argsort(tenors_arr)
    tenors_sorted = tenors_arr[sort_idx]
    rates_sorted = rates_arr[sort_idx]

    unique_tenors, unique_idx = np.unique(tenors_sorted, return_index=True)
    unique_rates = rates_sorted[unique_idx]
    return unique_tenors, unique_rates


