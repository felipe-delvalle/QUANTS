"""
Market Scanner
Scans markets for trading opportunities
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from ..config import AssetType
from ..data.market_symbols import Sector, MARKET_SYMBOLS
from ..api_clients.yahoo_finance import YahooFinanceClient
from ..data.historical_fetcher import HistoricalFetcher
from ..data.data_loader import DataLoader
from ..analysis.detailed_analyzer import DetailedAnalyzer

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_MAX_WORKERS = 20
DEFAULT_BATCH_SIZE = 50  # Batch size for quote fetching


class MarketScanner:
    """Scans markets for trading opportunities"""
    
    def __init__(self, data_loader=None, historical_fetcher=None, max_workers: int = DEFAULT_MAX_WORKERS):
        """
        Initialize market scanner
        
        Args:
            data_loader: DataLoader instance (optional)
            max_workers: Maximum number of parallel workers (default: 20)
        """
        self.data_loader = data_loader if data_loader is not None else DataLoader()
        self.yahoo_client = YahooFinanceClient()
        self.historical_fetcher = historical_fetcher if historical_fetcher is not None else HistoricalFetcher()
        self.analyzer = DetailedAnalyzer(self.data_loader)
        self.max_workers = max_workers
    
    def _process_symbol(
        self,
        symbol: str,
        asset_type_enum: AssetType,
        min_confidence: float,
        asset_type: str,
        current_price: Optional[float] = None,
        historical_data: Optional[pd.DataFrame] = None,
        full_analysis: bool = True,
        historical_years: float = 1.0
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single symbol to generate opportunity data
        
        Args:
            symbol: Stock symbol
            asset_type_enum: AssetType enum
            min_confidence: Minimum confidence threshold
            asset_type: Asset type string
            current_price: Pre-fetched price (optional, will fetch if None)
            historical_data: Pre-fetched historical data (optional, will fetch if None)
            full_analysis: Whether to run the heavyweight DetailedAnalyzer path
            historical_years: Years of history to fetch (lower for lightweight scans)
            
        Returns:
            Opportunity dictionary or None if filtered out
        """
        try:
            # Fetch real-time price if not provided
            if current_price is None:
                try:
                    quote = self.yahoo_client.get_quote(symbol)
                    current_price = float(quote.get("price", 0))
                    if current_price <= 0:
                        logger.warning(f"Invalid price for {symbol}: {current_price}, skipping")
                        return None
                except Exception as price_error:
                    logger.warning(f"Failed to fetch real-time price for {symbol}: {price_error}")
                    # Try to get from historical data as fallback
                    try:
                        fallback_data = self.historical_fetcher.fetch_historical_data(
                            symbol, asset_type_enum, years=0.5, use_cache=True
                        )
                        if fallback_data is not None and len(fallback_data) > 0:
                            current_price = float(fallback_data["close"].iloc[-1])
                        else:
                            logger.warning(f"No historical data available for {symbol}, skipping")
                            return None
                    except Exception as hist_error:
                        logger.warning(f"Failed to get historical price for {symbol}: {hist_error}")
                        return None
            
            # Fetch historical data for analysis if not provided
            if historical_data is None:
                try:
                    historical_data = self.historical_fetcher.fetch_historical_data(
                        symbol, asset_type_enum, years=historical_years, use_cache=True
                    )
                except Exception as hist_fetch_error:
                    logger.warning(f"Failed to fetch historical data for {symbol}: {hist_fetch_error}")
                    historical_data = None
            
            # Early filtering: Skip expensive analysis if we don't have enough data
            try:
                if not full_analysis:
                    # Lightweight path for dashboards: avoid full analyzer
                    closes = None
                    if historical_data is not None and len(historical_data) > 0:
                        closes = historical_data["close"] if "close" in historical_data.columns else historical_data.iloc[:, 0]
                    
                    signal = "HOLD"
                    trend = "neutral"
                    reasons = ["Quick scan"]
                    confidence = 0.55
                    
                    if closes is not None and len(closes) >= 20:
                        short_ma = closes.tail(20).mean()
                        long_ma = closes.tail(50).mean() if len(closes) >= 50 else closes.mean()
                        ma_gap = abs(short_ma - long_ma) / long_ma if long_ma else 0
                        
                        if current_price > short_ma and short_ma >= long_ma:
                            signal = "BUY"
                            trend = "uptrend"
                            reasons = ["Price above short-term trend", "Momentum improving"]
                        elif current_price < short_ma and short_ma <= long_ma:
                            signal = "SELL"
                            trend = "downtrend"
                            reasons = ["Price below short-term trend", "Momentum weakening"]
                        else:
                            reasons = ["Range-bound price action"]
                        
                        confidence = min(0.85, max(0.5, 0.55 + ma_gap))
                    else:
                        reasons = ["Quick scan with limited history"]
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
                return None
            
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
            
            logger.debug(f"Scanned {symbol}: {signal} @ ${current_price:.2f} (confidence: {confidence:.1%})")
            return opportunity
            
        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}", exc_info=True)
            return None
    
    def scan_stocks(
        self,
        symbols: List[str],
        min_confidence: float = 0.5,
        asset_type: str = "stock",
        period: str = "6mo",
        strategy: Optional[str] = None,
        full_analysis: bool = True,
        historical_years: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Scan stocks for trading opportunities using parallel processing and batch fetching
        
        Args:
            symbols: List of symbols to scan
            min_confidence: Minimum confidence threshold
            asset_type: Asset type (stock, crypto, forex, commodities)
            period: Time period for analysis
            full_analysis: Whether to run the heavyweight DetailedAnalyzer path
            historical_years: Years of history to fetch for analysis
            
        Returns:
            List of opportunity dictionaries with real prices and analysis
        """
        if not symbols:
            return []
        
        start_time = time.time()
        opportunities = []
        
        # Convert string asset_type to AssetType enum
        try:
            asset_type_enum = AssetType(asset_type) if isinstance(asset_type, str) else asset_type
        except (ValueError, TypeError):
            # Default to STOCK if conversion fails
            logger.warning(f"Invalid asset_type '{asset_type}', defaulting to STOCK")
            asset_type_enum = AssetType.STOCK
        
        # Step 1: Batch fetch prices for all symbols
        logger.info(f"Batch fetching prices for {len(symbols)} symbols...")
        price_start = time.time()
        price_data = {}
        try:
            # Fetch in batches to avoid overwhelming the API
            batch_size = DEFAULT_BATCH_SIZE
            batch_count = (len(symbols) + batch_size - 1) // batch_size
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                batch_num = i // batch_size + 1
                try:
                    batch_quotes = self.yahoo_client.get_quotes_batch(batch)
                    price_data.update(batch_quotes)
                    logger.debug(f"Fetched prices for batch {batch_num}/{batch_count} ({len(batch)} symbols, {len(batch_quotes)} successful)")
                except Exception as batch_error:
                    logger.warning(f"Batch fetch failed for batch {batch_num} ({len(batch)} symbols), falling back to individual: {batch_error}")
                    # Fallback: fetch individually for this batch
                    for sym in batch:
                        try:
                            price_data[sym] = self.yahoo_client.get_quote(sym)
                        except Exception:
                            continue
            price_elapsed = time.time() - price_start
            logger.info(f"Price fetching completed in {price_elapsed:.2f}s ({len(price_data)}/{len(symbols)} successful)")
        except Exception as e:
            logger.error(f"Error in batch price fetching: {e}, falling back to sequential")
            price_data = {}
        
        # Step 2: Batch fetch historical data for all symbols
        logger.info(f"Batch fetching historical data for {len(symbols)} symbols...")
        hist_start = time.time()
        historical_data_map = {}
        try:
            historical_data_map = self.historical_fetcher.fetch_historical_data_batch(
                symbols, asset_type_enum, years=historical_years, use_cache=True
            )
            hist_elapsed = time.time() - hist_start
            valid_data_count = sum(1 for v in historical_data_map.values() if v is not None and len(v) >= 50)
            logger.info(f"Historical data fetching completed in {hist_elapsed:.2f}s ({valid_data_count}/{len(symbols)} with sufficient data)")
        except Exception as hist_batch_error:
            logger.warning(f"Batch historical data fetch failed: {hist_batch_error}, will fetch individually")
            historical_data_map = {}
        
        # Step 3: Process symbols in parallel with ThreadPoolExecutor
        logger.info(f"Processing {len(symbols)} symbols with {self.max_workers} workers...")
        processed_count = 0
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all symbol processing tasks with pre-fetched data
            futures = {
                executor.submit(
                    self._process_symbol,
                    symbol,
                    asset_type_enum,
                    min_confidence,
                    asset_type,
                    price_data.get(symbol, {}).get("price") if price_data.get(symbol) else None,
                    historical_data_map.get(symbol),
                    full_analysis,
                    historical_years
                ): symbol
                for symbol in symbols
            }
            
            # Collect results as they complete
            for future in as_completed(futures):
                symbol = futures[future]
                try:
                    result = future.result(timeout=60)  # 60 second timeout per symbol (analysis can take time)
                    if result:
                        opportunities.append(result)
                    processed_count += 1
                    
                    # Progress logging for large batches
                    if processed_count % max(1, len(symbols) // 10) == 0 or processed_count == len(symbols):
                        progress_pct = (processed_count / len(symbols)) * 100
                        elapsed = time.time() - start_time
                        rate = processed_count / elapsed if elapsed > 0 else 0
                        eta = (len(symbols) - processed_count) / rate if rate > 0 else 0
                        logger.info(f"Progress: {processed_count}/{len(symbols)} ({progress_pct:.1f}%) | "
                                  f"Found: {len(opportunities)} opportunities | "
                                  f"Rate: {rate:.1f} symbols/s | ETA: {eta:.1f}s")
                except Exception as e:
                    logger.error(f"Error processing {symbol}: {e}", exc_info=True)
                    processed_count += 1
        
        elapsed_time = time.time() - start_time
        logger.info(f"Scanned {len(symbols)} symbols in {elapsed_time:.2f}s, found {len(opportunities)} opportunities ({elapsed_time/len(symbols):.3f}s per symbol)")
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
                asset_type="stock",
                full_analysis=False,
                historical_years=0.5
            )
            
            results[sector.value] = opportunities[:limit_per_sector]
        
        return results
