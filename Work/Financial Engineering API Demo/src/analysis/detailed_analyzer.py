"""
Detailed Analysis Module
Provides comprehensive analysis for individual symbols
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DetailedAnalyzer:
    """Generate comprehensive analysis for symbols"""
    
    def __init__(self, loader):
        """
        Initialize detailed analyzer
        
        Args:
            loader: DataLoader instance
        """
        self.loader = loader
    
    def generate_comprehensive_analysis(
        self,
        symbol: str,
        current_price: float,
        historical_data: pd.DataFrame,
        signal_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive analysis
        
        Args:
            symbol: Stock symbol
            current_price: Current price
            historical_data: Historical price data DataFrame
            signal_type: Optional signal type (BUY/SELL/HOLD)
            
        Returns:
            Analysis dictionary with recommendation, technical_analysis, risk_analysis
        """
        # Calculate returns
        if 'close' in historical_data.columns:
            closes = historical_data['close']
        else:
            closes = historical_data.iloc[:, 0] if len(historical_data.columns) > 0 else pd.Series([current_price])
        
        returns = closes.pct_change().dropna()
        
        # Calculate basic metrics
        volatility = returns.std() * np.sqrt(252)  # Annualized
        mean_return = returns.mean() * 252  # Annualized
        
        # Calculate risk metrics
        max_drawdown = self._calculate_max_drawdown(closes)
        sharpe_ratio = (mean_return - 0.02) / volatility if volatility > 0 else 0
        
        # Calculate recent returns (always needed for trend_strength calculation)
        recent_returns = returns.tail(20).mean() if len(returns) >= 20 else returns.mean()
        
        # Determine recommendation
        if signal_type:
            action = signal_type.upper()
            recommendation_text = action
        else:
            # Simple logic based on recent trend
            if recent_returns > 0.001:
                action = "BUY"
                recommendation_text = "Buy"
            elif recent_returns < -0.001:
                action = "SELL"
                recommendation_text = "Sell"
            else:
                action = "HOLD"
                recommendation_text = "Hold"
        
        # Calculate confidence based on volatility and trend strength
        trend_strength = abs(recent_returns) if len(returns) >= 20 else 0.5
        confidence = min(0.95, max(0.5, trend_strength * 10 + 0.5))
        
        # Calculate ATR for volatility measure (more appropriate than price std dev)
        if 'high' in historical_data.columns and 'low' in historical_data.columns:
            high = historical_data['high']
            low = historical_data['low']
            atr = self._calculate_atr(high, low, closes, period=14)
        else:
            # Fallback: use returns-based volatility as percentage
            atr = current_price * (returns.std() * np.sqrt(252) * 0.02)  # Conservative estimate
        
        # Calculate ATR percentage safely for logging
        atr_pct_for_log = (atr / current_price * 100) if current_price > 0 else 0.0
        logger.info(f"Price calculation for {symbol}: current_price=${current_price:.2f}, ATR=${atr:.2f} ({atr_pct_for_log:.1f}% of price)")
        
        # Apply percentage caps to ATR
        atr_pct = (atr / current_price) if current_price > 0 else 0.02
        # Cap ATR percentage between 1% and 10%
        atr_pct = max(0.01, min(0.10, atr_pct))
        
        # Entry range: ±2-5% of current price
        entry_pct = min(0.05, max(0.02, atr_pct * 2))
        entry_min = current_price * (1 - entry_pct)
        entry_max = current_price * (1 + entry_pct)
        entry_range = f"${entry_min:.2f}-${entry_max:.2f}"
        
        # Calculate stop loss and targets with percentage caps
        if action == "BUY":
            # Stop loss: 5-15% below current price
            stop_loss_pct = min(0.15, max(0.05, atr_pct * 3))
            stop_loss = current_price * (1 - stop_loss_pct)
            
            # Targets: 10%, 20%, 30% above current price
            target1 = current_price * 1.10
            target2 = current_price * 1.20
            target3 = current_price * 1.30
        elif action == "SELL":
            # Stop loss: 5-15% above current price
            stop_loss_pct = min(0.15, max(0.05, atr_pct * 3))
            stop_loss = current_price * (1 + stop_loss_pct)
            
            # Targets: 10%, 20%, 30% below current price
            target1 = current_price * 0.90
            target2 = current_price * 0.80
            target3 = current_price * 0.70
        else:  # HOLD
            # Neutral: smaller ranges
            stop_loss = current_price * 0.95
            target1 = current_price * 1.05
            target2 = current_price * 1.10
            target3 = current_price * 1.15
        
        # Format as strings
        stop_loss = f"${stop_loss:.2f}"
        target1 = f"${target1:.2f}"
        target2 = f"${target2:.2f}"
        target3 = f"${target3:.2f}"
        
        logger.info(f"Calculated for {symbol}: stop_loss={stop_loss}, targets=[{target1}, {target2}, {target3}]")
        
        # Calculate RSI
        rsi = self._calculate_rsi(closes, period=14)
        rsi_value = rsi.iloc[-1] if len(rsi) > 0 else 50
        if rsi_value > 70:
            rsi_signal = "overbought"
        elif rsi_value < 30:
            rsi_signal = "oversold"
        else:
            rsi_signal = "neutral"
        
        # Determine trend
        sma_20 = closes.rolling(20).mean().iloc[-1] if len(closes) >= 20 else current_price
        sma_50 = closes.rolling(50).mean().iloc[-1] if len(closes) >= 50 else current_price
        
        if sma_20 > sma_50:
            trend = "uptrend"
            macd_signal = "bullish"
        else:
            trend = "downtrend"
            macd_signal = "bearish"
        
        # Risk score (0-1, lower is better)
        risk_score = min(1.0, max(0.0, (volatility * 2 + abs(max_drawdown) * 2) / 2))
        
        # Risk rating
        if risk_score < 0.3:
            risk_rating = "Low Risk"
        elif risk_score < 0.6:
            risk_rating = "Medium Risk"
        else:
            risk_rating = "High Risk"
        
        return {
            "symbol": symbol,
            "current_price": current_price,
            "recommendation": {
                "recommendation": recommendation_text,
                "action": action,
                "confidence": confidence,
                "timeframe": "3-6 months",
                "entry_range": entry_range,
                "stop_loss": stop_loss,
                "targets": [target1, target2, target3],
                "risk_reward_ratio": 2.5,
                "trend": trend,
                "symbol": symbol
            },
            "technical_analysis": {
                "indicators": {
                    "rsi": {
                        "value": float(rsi_value),
                        "signal": rsi_signal
                    },
                    "macd": {
                        "signal": macd_signal
                    }
                },
                "trend": trend
            },
            "risk_analysis": {
                "risk_score": float(risk_score),
                "risk_rating": risk_rating,
                "volatility": {
                    "annual": float(volatility)
                },
                "max_drawdown": float(max_drawdown),
                "sharpe_ratio": float(sharpe_ratio)
            },
            "historical_performance": {}
        }
    
    def _calculate_max_drawdown(self, prices: pd.Series) -> float:
        """Calculate maximum drawdown"""
        if len(prices) < 2:
            return 0.0
        
        cumulative = (1 + prices.pct_change()).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        return float(drawdown.min())
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return pd.Series([50.0] * len(prices), index=prices.index)
        
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50.0)
    
    def _calculate_atr(self, high: pd.Series, low: pd.Series, close: pd.Series, period: int = 14) -> float:
        """
        Calculate Average True Range (ATR) for volatility measure
        
        Args:
            high: High prices series
            low: Low prices series
            close: Close prices series
            period: ATR period (default 14)
        
        Returns:
            ATR value as float
        """
        if len(high) < period + 1:
            # Fallback: use simple price range if not enough data
            return float((high - low).mean()) if len(high) > 0 else float(close.iloc[-1] * 0.02)
        
        # Calculate True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        true_range = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Calculate ATR as moving average of True Range
        atr = true_range.rolling(window=period).mean().iloc[-1]
        
        return float(atr) if not pd.isna(atr) else float((high - low).mean())


class ReportGenerator:
    """Generate text reports from analysis"""
    
    def __init__(self):
        """Initialize report generator"""
        pass
    
    def _generate_executive_summary(self, symbol: str, analysis: Dict[str, Any]) -> str:
        """
        Generate executive summary text
        
        Args:
            symbol: Stock symbol
            analysis: Analysis dictionary
            
        Returns:
            Executive summary text
        """
        rec = analysis.get("recommendation", {})
        risk = analysis.get("risk_analysis", {})
        
        action = rec.get("action", "HOLD")
        confidence = rec.get("confidence", 0.5) * 100
        risk_rating = risk.get("risk_rating", "Medium Risk")
        
        summary = f"""
Based on comprehensive technical and quantitative analysis, {symbol} exhibits {rec.get('trend', 'neutral')} characteristics 
with a confidence level of {confidence:.0f}%. The current market structure suggests a {rec.get('timeframe', 'medium-term')} 
outlook with entry opportunities in the {rec.get('entry_range', 'N/A')} range. 

Key resistance levels are identified at {', '.join(rec.get('targets', ['N/A'])[:2])}, while risk management suggests 
a stop loss at {rec.get('stop_loss', 'N/A')}. The risk assessment indicates {risk_rating.lower()}, making this suitable 
for {action.lower()} positions with appropriate position sizing.
        """.strip()
        
        return summary

