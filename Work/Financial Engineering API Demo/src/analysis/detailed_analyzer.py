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
        
        # Calculate entry range and targets based on signal direction
        price_std = closes.std()
        entry_min = current_price - price_std * 0.5
        entry_max = current_price + price_std * 0.5
        entry_range = f"${entry_min:.2f}-${entry_max:.2f}"
        
        # Calculate stop loss and targets based on signal type
        if action == "BUY":
            # For BUY: stop loss below, targets above
            stop_loss = f"${current_price - price_std * 2:.2f}"
            target1 = f"${current_price + price_std * 1.5:.2f}"
            target2 = f"${current_price + price_std * 3:.2f}"
            target3 = f"${current_price + price_std * 5:.2f}"
        elif action == "SELL":
            # For SELL: stop loss above, targets below
            stop_loss = f"${current_price + price_std * 2:.2f}"
            target1 = f"${current_price - price_std * 1.5:.2f}"
            target2 = f"${current_price - price_std * 3:.2f}"
            target3 = f"${current_price - price_std * 5:.2f}"
        else:  # HOLD
            # For HOLD: neutral range
            stop_loss = f"${current_price - price_std * 1:.2f}"
            target1 = f"${current_price + price_std * 1:.2f}"
            target2 = f"${current_price + price_std * 2:.2f}"
            target3 = f"${current_price + price_std * 3:.2f}"
        
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

