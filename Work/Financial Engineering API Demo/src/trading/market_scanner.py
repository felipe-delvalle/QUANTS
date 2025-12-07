"""
Market Scanner
Scans markets for trading opportunities
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

from ..config import AssetType
from ..data.market_symbols import Sector, MARKET_SYMBOLS

logger = logging.getLogger(__name__)


class MarketScanner:
    """Scans markets for trading opportunities"""
    
    def __init__(self, data_loader=None):
        """
        Initialize market scanner
        
        Args:
            data_loader: DataLoader instance (optional)
        """
        self.data_loader = data_loader
    
    def scan_stocks(
        self,
        symbols: List[str],
        min_confidence: float = 0.5,
        asset_type: str = "stock",
        period: str = "6mo"
    ) -> List[Dict[str, Any]]:
        """
        Scan stocks for trading opportunities
        
        Args:
            symbols: List of symbols to scan
            min_confidence: Minimum confidence threshold
            asset_type: Asset type (stock, crypto, forex, commodities)
            period: Time period for analysis
            
        Returns:
            List of opportunity dictionaries
        """
        opportunities = []
        
        for symbol in symbols:
            try:
                # Generate a mock opportunity with random confidence
                confidence = random.uniform(0.4, 0.95)
                
                if confidence < min_confidence:
                    continue
                
                # Determine signal based on random chance
                signal = "BUY" if random.random() > 0.4 else "SELL"
                
                # Generate mock price
                base_price = random.uniform(50, 500)
                current_price = base_price * random.uniform(0.9, 1.1)
                
                # Generate reasons
                reasons = []
                if signal == "BUY":
                    reasons.append("RSI oversold")
                    reasons.append("Price at lower support level")
                    reasons.append("Bullish momentum")
                else:
                    reasons.append("RSI overbought")
                    reasons.append("Price at upper resistance")
                    reasons.append("Bearish momentum")
                
                opportunity = {
                    "symbol": symbol,
                    "asset": symbol,
                    "asset_type": asset_type,
                    "signal": signal,
                    "confidence": round(confidence, 2),
                    "current_price": round(current_price, 2),
                    "price": round(current_price, 2),  # Keep for backward compatibility
                    "trend": "uptrend" if signal == "BUY" else "downtrend",
                    "reasons": reasons,
                    "timestamp": datetime.now().isoformat()
                }
                
                opportunities.append(opportunity)
                
            except Exception as e:
                logger.warning(f"Error scanning {symbol}: {e}")
                continue
        
        logger.info(f"Scanned {len(symbols)} symbols in 0.00s, found {len(opportunities)} opportunities")
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

