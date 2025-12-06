"""
Portfolio Analysis
Calculate portfolio metrics and performance
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class PortfolioAnalyzer:
    """Analyze portfolio performance and metrics"""

    def __init__(self, symbols: List[str], weights: List[float] = None):
        """
        Initialize portfolio analyzer

        Args:
            symbols: List of stock symbols
            weights: Portfolio weights (default: equal weights)
        """
        self.symbols = symbols
        self.weights = (
            np.array(weights)
            if weights
            else np.array([1.0 / len(symbols)] * len(symbols))
        )

        if len(self.weights) != len(symbols):
            raise ValueError("Weights length must match symbols length")

        if not np.isclose(self.weights.sum(), 1.0):
            raise ValueError("Weights must sum to 1.0")

    def calculate_returns(self, prices: pd.DataFrame) -> pd.Series:
        """
        Calculate portfolio returns

        Args:
            prices: DataFrame with prices for each symbol

        Returns:
            Portfolio returns series
        """
        returns = prices.pct_change().dropna()
        portfolio_returns = (returns * self.weights).sum(axis=1)
        return portfolio_returns

    def calculate_risk_metrics(
        self, returns: pd.Series, risk_free_rate: float = 0.02
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk metrics

        Args:
            returns: Portfolio returns series
            risk_free_rate: Annual risk-free rate

        Returns:
            Dictionary of risk metrics
        """
        annual_returns = returns.mean() * 252
        annual_volatility = returns.std() * np.sqrt(252)

        # Sharpe Ratio
        sharpe_ratio = (annual_returns - risk_free_rate) / annual_volatility

        # Maximum Drawdown
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # Value at Risk (VaR) - 95% confidence
        var_95 = np.percentile(returns, 5)

        # Conditional VaR (CVaR) - Expected loss beyond VaR
        cvar_95 = returns[returns <= var_95].mean()

        return {
            "annual_return": float(annual_returns),
            "annual_volatility": float(annual_volatility),
            "sharpe_ratio": float(sharpe_ratio),
            "max_drawdown": float(max_drawdown),
            "var_95": float(var_95),
            "cvar_95": float(cvar_95),
            "skewness": float(returns.skew()),
            "kurtosis": float(returns.kurtosis()),
        }

    def analyze_portfolio(
        self, prices: pd.DataFrame, risk_free_rate: float = 0.02
    ) -> Dict[str, Any]:
        """
        Complete portfolio analysis

        Args:
            prices: DataFrame with prices for each symbol
            risk_free_rate: Annual risk-free rate

        Returns:
            Complete analysis results
        """
        returns = self.calculate_returns(prices)
        risk_metrics = self.calculate_risk_metrics(returns, risk_free_rate)

        return {
            "symbols": self.symbols,
            "weights": self.weights.tolist(),
            "returns": {
                "total_return": float((1 + returns).prod() - 1),
                "annualized_return": float(risk_metrics["annual_return"]),
                "daily_mean": float(returns.mean()),
                "daily_std": float(returns.std()),
            },
            "risk_metrics": risk_metrics,
            "correlation_matrix": prices.pct_change().corr().to_dict(),
        }
