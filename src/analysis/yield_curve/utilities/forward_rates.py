from __future__ import annotations

def forward_rate_from_dfs(df1: float, df2: float, t1: float, t2: float) -> float:
    """
    Compute forward rate implied by two discount factors.
    """
    if t2 <= t1:
        raise ValueError("t2 must be greater than t1")
    return (df1 / df2 - 1.0) / (t2 - t1)


def forward_rate_from_spots(r1: float, r2: float, t1: float, t2: float, continuous: bool = False) -> float:
    """
    Compute forward rate from spot rates using simple or continuous compounding.
    """
    if t2 <= t1:
        raise ValueError("t2 must be greater than t1")
    if continuous:
        return (r2 * t2 - r1 * t1) / (t2 - t1)
    df1 = 1.0 / (1.0 + r1 * t1)
    df2 = 1.0 / (1.0 + r2 * t2)
    return forward_rate_from_dfs(df1, df2, t1, t2)


