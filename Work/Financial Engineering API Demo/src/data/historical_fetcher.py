"""
Historical Data Fetcher
Fetches historical market data
"""

import logging
from typing import Optional
import pandas as pd
from datetime import datetime, timedelta

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False

from ..config import AssetType

logger = logging.getLogger(__name__)


class HistoricalFetcher:
    """Fetches historical market data"""
    
    def __init__(self):
        """Initialize historical fetcher"""
        self.cache = {}
    
    def fetch_historical_data(
        self,
        symbol: str,
        asset_type: AssetType,
        years: float = 1.0,
        use_cache: bool = True
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical data for a symbol
        
        Args:
            symbol: Stock/crypto/forex symbol
            asset_type: Asset type enum
            years: Number of years of data to fetch
            use_cache: Whether to use cached data
            
        Returns:
            DataFrame with historical data (columns: open, high, low, close, volume)
        """
        cache_key = f"{symbol}_{asset_type.value}_{years}"
        
        if use_cache and cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            if not YFINANCE_AVAILABLE:
                logger.warning("yfinance not available, generating sample data")
                return self._generate_sample_data(symbol, years)
            
            # Fetch data using yfinance
            period_map = {
                0.003: "1d", 0.019: "5d", 0.083: "1mo",
                0.25: "3mo", 0.5: "6mo", 1.0: "1y", 5.0: "5y"
            }
            
            # Find closest period
            period = "1y"
            for y, p in sorted(period_map.items(), reverse=True):
                if years >= y:
                    period = p
                    break
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                logger.warning(f"No data for {symbol}, generating sample data")
                return self._generate_sample_data(symbol, years)
            
            # Ensure required columns exist
            if 'Volume' in hist.columns:
                hist = hist.rename(columns={'Volume': 'volume'})
            else:
                hist['volume'] = 0
            
            # Rename columns to lowercase
            hist.columns = [col.lower() for col in hist.columns]
            
            # Ensure we have the required columns
            required_cols = ['open', 'high', 'low', 'close']
            for col in required_cols:
                if col not in hist.columns:
                    hist[col] = hist.get('close', hist.iloc[:, 0] if len(hist.columns) > 0 else 0)
            
            if use_cache:
                self.cache[cache_key] = hist
            
            return hist
            
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            return self._generate_sample_data(symbol, years)
    
    def _generate_sample_data(self, symbol: str, years: float) -> pd.DataFrame:
        """Generate sample data for testing"""
        import numpy as np
        
        days = int(years * 365)
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        # Generate random walk price data
        np.random.seed(hash(symbol) % 2**32)
        base_price = 100.0
        returns = np.random.randn(days) * 0.02
        prices = base_price * (1 + returns).cumprod()
        
        data = pd.DataFrame({
            'open': prices * (1 + np.random.randn(days) * 0.005),
            'high': prices * (1 + abs(np.random.randn(days)) * 0.01),
            'low': prices * (1 - abs(np.random.randn(days)) * 0.01),
            'close': prices,
            'volume': np.random.randint(1000000, 10000000, days)
        }, index=dates)
        
        return data
    
    def get_signal_performance(self, symbol: str, lookback_days: int = 365) -> dict:
        """
        Get signal performance history
        
        Args:
            symbol: Stock symbol
            lookback_days: Number of days to look back
            
        Returns:
            Dictionary with signal performance data
        """
        # Placeholder implementation
        return {
            "symbol": symbol,
            "total_signals": 0,
            "win_rate": 0.0,
            "avg_return": 0.0
        }
