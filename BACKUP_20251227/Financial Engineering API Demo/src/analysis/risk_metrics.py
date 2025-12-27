"""
Risk Metrics Calculator
Calculate various risk metrics for portfolios
"""

import numpy as np
import pandas as pd
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class RiskCalculator:
    """Calculate risk metrics"""

    @staticmethod
    def calculate_var(returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)

        Args:
            returns: Returns series
            confidence: Confidence level (0.95 for 95%)

        Returns:
            VaR value
        """
        return float(np.percentile(returns, (1 - confidence) * 100))

    @staticmethod
    def calculate_cvar(returns: pd.Series, confidence: float = 0.95) -> float:
        """
        Calculate Conditional VaR (CVaR) / Expected Shortfall

        Args:
            returns: Returns series
            confidence: Confidence level

        Returns:
            CVaR value
        """
        var = RiskCalculator.calculate_var(returns, confidence)
        return float(returns[returns <= var].mean())

    @staticmethod
    def calculate_beta(portfolio_returns: pd.Series, market_returns: pd.Series) -> float:
        """
        Calculate portfolio beta

        Args:
            portfolio_returns: Portfolio returns
            market_returns: Market returns (e.g., S&P 500)

        Returns:
            Beta value
        """
        covariance = np.cov(portfolio_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)
        return float(covariance / market_variance)
