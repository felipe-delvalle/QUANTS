"""
Market Scanner
Scans markets for trading opportunities
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd

from ..config import AssetType
from ..data.market_symbols import Sector, MARKET_SYMBOLS
from ..api_clients.yahoo_finance import YahooFinanceClient
from ..data.historical_fetcher import HistoricalFetcher
from ..data.data_loader import DataLoader
from ..analysis.detailed_analyzer import DetailedAnalyzer

logger = logging.getLogger(__name__)


class MarketScanner:
    """Scans markets for trading opportunities"""
    
    def __init__(self, data_loader=None):
        """
        Initialize market scanner
        
        Args:
            data_loader: DataLoader instance (optional)
        """
        self.data_loader = data_loader if data_loader is not None else DataLoader()
        self.yahoo_client = YahooFinanceClient()
        self.historical_fetcher = HistoricalFetcher()
        self.analyzer = DetailedAnalyzer(self.data_loader)
    
    def scan_stocks(
        self,
        symbols: List[str],
        min_confidence: float = 0.5,
        asset_type: str = "stock",
        period: str = "6mo"
    ) -> List[Dict[str, Any]]:
        """
        Scan stocks for trading opportunities using real-time data and analysis
        
        Args:
            symbols: List of symbols to scan
            min_confidence: Minimum confidence threshold
            asset_type: Asset type (stock, crypto, forex, commodities)
            period: Time period for analysis
            
        Returns:
            List of opportunity dictionaries with real prices and analysis
        """
        opportunities = []
        
        # Convert string asset_type to AssetType enum
        try:
            asset_type_enum = AssetType(asset_type) if isinstance(asset_type, str) else asset_type
        except (ValueError, TypeError):
            # Default to STOCK if conversion fails
            logger.warning(f"Invalid asset_type '{asset_type}', defaulting to STOCK")
            asset_type_enum = AssetType.STOCK
        
        for symbol in symbols:
            try:
                # Fetch real-time price
                try:
                    quote = self.yahoo_client.get_quote(symbol)
                    current_price = float(quote.get("price", 0))
                    if current_price <= 0:
                        logger.warning(f"Invalid price for {symbol}: {current_price}, skipping")
                        continue
                except Exception as price_error:
                    logger.warning(f"Failed to fetch real-time price for {symbol}: {price_error}")
                    # Try to get from historical data as fallback
                    try:
                        historical_data = self.historical_fetcher.fetch_historical_data(
                            symbol, asset_type_enum, years=0.5, use_cache=True
                        )
                        if historical_data is not None and len(historical_data) > 0:
                            current_price = float(historical_data["close"].iloc[-1])
                        else:
                            logger.warning(f"No historical data available for {symbol}, skipping")
                            continue
                    except Exception as hist_error:
                        logger.warning(f"Failed to get historical price for {symbol}: {hist_error}")
                        continue
                
                # Fetch historical data for analysis
                try:
                    historical_data = self.historical_fetcher.fetch_historical_data(
                        symbol, asset_type_enum, years=1, use_cache=True
                    )
                    
                    if historical_data is None or len(historical_data) < 50:
                        logger.warning(f"Insufficient historical data for {symbol}, using basic analysis")
                        # Use basic analysis with just price
                        signal = "HOLD"
                        confidence = 0.5
                        trend = "neutral"
                        reasons = ["Insufficient data for full analysis"]
                    else:
                        # Generate comprehensive analysis
                        analysis = self.analyzer.generate_comprehensive_analysis(
                            symbol=symbol,
                            current_price=current_price,
                            historical_data=historical_data
                        )
                        
                        # Extract signal and confidence from analysis
                        recommendation = analysis.get("recommendation", {})
                        signal = recommendation.get("action", "HOLD")
                        confidence = float(recommendation.get("confidence", 0.5))
                        trend = recommendation.get("trend", "neutral")
                        
                        # Generate reasons from technical analysis
                        technical = analysis.get("technical_analysis", {})
                        indicators = technical.get("indicators", {})
                        reasons = []
                        
                        # RSI-based reasons
                        rsi_data = indicators.get("rsi", {})
                        rsi_value = rsi_data.get("value", 50)
                        rsi_signal = rsi_data.get("signal", "neutral")
                        if rsi_signal == "oversold":
                            reasons.append("RSI oversold")
                        elif rsi_signal == "overbought":
                            reasons.append("RSI overbought")
                        
                        # MACD-based reasons
                        macd_data = indicators.get("macd", {})
                        macd_signal = macd_data.get("signal", "neutral")
                        if macd_signal == "bullish":
                            reasons.append("Bullish momentum")
                        elif macd_signal == "bearish":
                            reasons.append("Bearish momentum")
                        
                        # Trend-based reasons
                        if trend == "uptrend":
                            reasons.append("Price at lower support level")
                        elif trend == "downtrend":
                            reasons.append("Price at upper resistance")
                        
                        # Ensure we have at least one reason
                        if not reasons:
                            reasons.append(f"{trend.capitalize()} trend")
                
                except Exception as analysis_error:
                    logger.warning(f"Error analyzing {symbol}: {analysis_error}")
                    # Fallback to basic data
                    signal = "HOLD"
                    confidence = 0.5
                    trend = "neutral"
                    reasons = ["Analysis unavailable"]
                
                # Filter by minimum confidence
                if confidence < min_confidence:
                    continue
                
                # Create opportunity with real data
                # Ensure reasons is a list for categorization
                if not isinstance(reasons, list):
                    reasons = [reasons] if reasons else []
                
                opportunity = {
                    "symbol": symbol,
                    "asset": asset_type.upper(),
                    "asset_type": asset_type,
                    "signal": signal,
                    "confidence": round(confidence, 3),  # 3 decimal places for percentage display
                    "current_price": round(current_price, 2),
                    "price": round(current_price, 2),  # Keep for backward compatibility
                    "trend": trend,
                    "reasons": reasons,  # Keep as list for categorization
                    "timestamp": datetime.now().isoformat()
                }
                
                opportunities.append(opportunity)
                logger.debug(f"Scanned {symbol}: {signal} @ ${current_price:.2f} (confidence: {confidence:.1%})")
                
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}", exc_info=True)
                continue
        
        logger.info(f"Scanned {len(symbols)} symbols, found {len(opportunities)} opportunities")
        return opportunities
    
    def scan_by_sectors(
        self,
        sectors: List[Sector],
        min_confidence: float = 0.5,
        strategy: Optional[str] = None,
        limit_per_sector: int = 10,
        use_cache: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan stocks by sectors
        
        Args:
            sectors: List of Sector enums
            min_confidence: Minimum confidence threshold
            strategy: Optional strategy name
            limit_per_sector: Maximum opportunities per sector
            use_cache: Whether to use cache
            
        Returns:
            Dictionary mapping sector names to opportunity lists
        """
        results = {}
        
        for sector in sectors:
            symbols = MARKET_SYMBOLS.get(sector, [])
            if not symbols:
                results[sector.value] = []
                continue
            
            opportunities = self.scan_stocks(
                symbols=symbols,
                min_confidence=min_confidence,
                asset_type="stock"
            )
            
            results[sector.value] = opportunities[:limit_per_sector]
        
        return results

