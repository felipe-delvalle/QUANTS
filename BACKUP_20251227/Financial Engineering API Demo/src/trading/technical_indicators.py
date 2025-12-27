"""
Technical Indicators
Provides technical analysis indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Technical analysis indicators"""
    
    def __init__(self, close: pd.Series):
        """
        Initialize technical analyzer
        
        Args:
            close: Series of closing prices
        """
        self.close = close
        self.high = None
        self.low = None
        self.volume = None
    
    def set_ohlcv(self, high: Optional[pd.Series] = None,
                  low: Optional[pd.Series] = None,
                  volume: Optional[pd.Series] = None):
        """
        Set OHLCV data
        
        Args:
            high: High prices
            low: Low prices
            volume: Volume data
        """
        self.high = high if high is not None else self.close
        self.low = low if low is not None else self.close
        self.volume = volume
    
    def comprehensive_analysis(self) -> Dict[str, Any]:
        """
        Perform comprehensive technical analysis
        
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "moving_averages": self._calculate_moving_averages(),
            "current_rsi": self._calculate_rsi().iloc[-1] if len(self.close) > 14 else 50.0,
            "macd": self._calculate_macd()
        }
        return analysis
    
    def _calculate_moving_averages(self) -> Dict[str, pd.Series]:
        """Calculate moving averages"""
        return {
            "ma_20": self.close.rolling(window=20).mean(),
            "ma_50": self.close.rolling(window=50).mean(),
            "ma_200": self.close.rolling(window=200).mean()
        }
    
    def _calculate_rsi(self, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = self.close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)
    
    def _calculate_macd(self) -> Dict[str, pd.Series]:
        """Calculate MACD"""
        ema_12 = self.close.ewm(span=12, adjust=False).mean()
        ema_26 = self.close.ewm(span=26, adjust=False).mean()
        macd = ema_12 - ema_26
        signal = macd.ewm(span=9, adjust=False).mean()
        
        return {
            "macd": macd,
            "signal": signal,
            "histogram": macd - signal
        }
