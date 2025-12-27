from __future__ import annotations

from typing import Callable


def par_yield(
    discount_factor_fn: Callable[[float], float],
    maturity: float,
    frequency: int = 2,
    face_value: float = 100.0,
) -> float:
    """
    Compute par yield for a given maturity using discount factors.
    """
    if maturity <= 0:
        raise ValueError("Maturity must be positive")
    periods = int(round(maturity * frequency))
    if periods == 0:
        raise ValueError("Periods computed to zero; check maturity/frequency")

    coupon_times = [(i + 1) / frequency for i in range(periods)]
    dfs = [discount_factor_fn(t) for t in coupon_times]

    annuity = sum(dfs)
    df_final = dfs[-1]

    return (face_value * (1 - df_final) / annuity) / face_value


