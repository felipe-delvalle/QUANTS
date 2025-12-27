"""
Portfolio Optimization
Optimize portfolio weights using various strategies
"""

import numpy as np
from scipy.optimize import minimize
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    """Optimize portfolio allocation"""

    @staticmethod
    def optimize_sharpe(
        returns: np.ndarray, risk_free_rate: float = 0.02
    ) -> Dict[str, Any]:
        """
        Optimize portfolio for maximum Sharpe ratio

        Args:
            returns: Returns matrix (n_assets x n_periods)
            risk_free_rate: Risk-free rate

        Returns:
            Optimized weights and metrics
        """
        n_assets = returns.shape[0]
        
        def negative_sharpe(weights):
            portfolio_return = np.dot(weights, returns.mean(axis=1))
            portfolio_std = np.sqrt(
                np.dot(weights.T, np.dot(np.cov(returns), weights))
            )
            sharpe = (portfolio_return - risk_free_rate) / portfolio_std
            return -sharpe

        constraints = {"type": "eq", "fun": lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1.0 / n_assets] * n_assets)

        result = minimize(
            negative_sharpe,
            initial_weights,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints,
        )

        return {
            "weights": result.x.tolist(),
            "sharpe_ratio": -result.fun,
            "success": result.success,
        }
