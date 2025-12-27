"""
Backtesting Engine
Backtests trading strategies on historical data
"""

import logging
from typing import Dict, Any, Optional, List
import pandas as pd

logger = logging.getLogger(__name__)


class BacktestEngine:
    """Backtesting engine for trading strategies"""
    
    def __init__(self, fee_bps: float = 10.0, slippage_bps: float = 5.0):
        """
        Initialize backtesting engine
        
        Args:
            fee_bps: Trading fees in basis points (default 10 bps = 0.1%)
            slippage_bps: Slippage in basis points (default 5 bps = 0.05%)
        """
        self.fee_bps = fee_bps
        self.slippage_bps = slippage_bps
    
    def run_backtest(
        self,
        symbol: str,
        strategy: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run backtest for a strategy
        
        Args:
            symbol: Stock symbol
            strategy: Strategy name
            start_date: Start date (optional)
            end_date: End date (optional)
            
        Returns:
            Backtest results dictionary
        """
        # Basic implementation - can be enhanced later
        return {
            "symbol": symbol,
            "strategy": strategy,
            "total_return": 0.0,
            "sharpe_ratio": 0.0,
            "max_drawdown": 0.0,
            "trades": []
        }
    
    def backtest_signals(self, price_series: pd.Series, signals: pd.Series):
        """
        Backtest trading signals on price series
        
        Args:
            price_series: Series of prices
            signals: Series of trading signals (0 = no position, 1 = long position)
            
        Returns:
            Object with .metrics, .equity_curve, and .returns attributes
        """
        if len(price_series) != len(signals):
            raise ValueError("price_series and signals must have same length")
        
        if len(price_series) == 0:
            raise ValueError("price_series cannot be empty")
        
        # Align indices
        aligned_prices = price_series.reindex(signals.index, method='ffill')
        aligned_signals = signals.fillna(0)
        
        # Calculate returns
        price_returns = aligned_prices.pct_change().fillna(0)
        
        # Calculate position returns (only when signal is 1)
        position_returns = price_returns * aligned_signals
        
        # Apply fees and slippage
        fee_multiplier = 1 - (self.fee_bps / 10000)
        slippage_multiplier = 1 - (self.slippage_bps / 10000)
        adjusted_returns = position_returns * fee_multiplier * slippage_multiplier
        
        # Calculate equity curve (cumulative returns)
        equity_curve = (1 + adjusted_returns).cumprod()
        
        # Calculate total return
        total_return = float(equity_curve.iloc[-1] - 1) if len(equity_curve) > 0 else 0.0
        
        # Calculate Sharpe ratio (annualized)
        if len(adjusted_returns) > 1:
            mean_return = adjusted_returns.mean() * 252  # Annualized
            std_return = adjusted_returns.std() * (252 ** 0.5)  # Annualized
            sharpe_ratio = mean_return / std_return if std_return > 0 else 0.0
        else:
            sharpe_ratio = 0.0
        
        # Calculate max drawdown
        if len(equity_curve) > 0:
            running_max = equity_curve.expanding().max()
            drawdown = (equity_curve - running_max) / running_max
            max_drawdown = float(drawdown.min())
        else:
            max_drawdown = 0.0
        
        # Create result object with required attributes
        class BacktestResult:
            def __init__(self):
                self.metrics = {
                    "total_return": total_return,
                    "sharpe_ratio": sharpe_ratio,
                    "max_drawdown": max_drawdown
                }
                self.equity_curve = equity_curve
                self.returns = adjusted_returns
        
        return BacktestResult()

