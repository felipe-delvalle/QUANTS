"""
Yahoo Finance API Client
Provides market data using yfinance library
"""

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    yf = None

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class YahooFinanceClient:
    """Client for Yahoo Finance data using yfinance"""

    def __init__(self):
        """Initialize Yahoo Finance client"""
        pass

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote for a symbol

        Args:
            symbol: Stock symbol

        Returns:
            Quote data dictionary
        """
        if not YFINANCE_AVAILABLE:
            raise ImportError("yfinance not installed. Install with: pip install yfinance")
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            quote = ticker.history(period="1d").iloc[-1]

            return {
                "symbol": symbol,
                "price": float(quote["Close"]),
                "change": float(quote["Close"] - quote["Open"]),
                "change_percent": (
                    (quote["Close"] - quote["Open"]) / quote["Open"] * 100
                ),
                "volume": int(quote["Volume"]),
                "high": float(quote["High"]),
                "low": float(quote["Low"]),
                "open": float(quote["Open"]),
                "previous_close": float(info.get("previousClose", 0)),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
            }
        except Exception as e:
            logger.error(f"Error fetching quote for {symbol}: {e}")
            raise
    
    def _extract_quote(self, ticker: Any, symbol: str) -> Dict[str, Any]:
        """
        Extract quote data from a yfinance Ticker object
        
        Args:
            ticker: yfinance Ticker object
            symbol: Stock symbol
            
        Returns:
            Quote data dictionary
        """
        try:
            info = ticker.info
            hist = ticker.history(period="1d")
            if len(hist) == 0:
                raise ValueError(f"No data available for {symbol}")
            quote = hist.iloc[-1]
            
            return {
                "symbol": symbol,
                "price": float(quote["Close"]),
                "change": float(quote["Close"] - quote["Open"]),
                "change_percent": (
                    (quote["Close"] - quote["Open"]) / quote["Open"] * 100
                ) if quote["Open"] > 0 else 0.0,
                "volume": int(quote["Volume"]),
                "high": float(quote["High"]),
                "low": float(quote["Low"]),
                "open": float(quote["Open"]),
                "previous_close": float(info.get("previousClose", 0)),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "dividend_yield": info.get("dividendYield"),
            }
        except Exception as e:
            logger.error(f"Error extracting quote for {symbol}: {e}")
            raise
    
    def get_quotes_batch(self, symbols: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Fetch quotes for multiple symbols in one batch call
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            Dictionary mapping symbol to quote data
        """
        if not YFINANCE_AVAILABLE:
            raise ImportError("yfinance not installed. Install with: pip install yfinance")
        
        if not symbols:
            return {}
        
        try:
            # Use yf.Tickers for batch fetching
            tickers = yf.Tickers(" ".join(symbols))
            quotes = {}
            
            for symbol in symbols:
                try:
                    if symbol in tickers.tickers:
                        quotes[symbol] = self._extract_quote(tickers.tickers[symbol], symbol)
                    else:
                        logger.warning(f"Symbol {symbol} not found in batch fetch, trying individual fetch")
                        # Fallback to individual fetch
                        quotes[symbol] = self.get_quote(symbol)
                except Exception as e:
                    logger.warning(f"Failed to fetch quote for {symbol} in batch: {e}")
                    # Try individual fetch as fallback
                    try:
                        quotes[symbol] = self.get_quote(symbol)
                    except Exception as fallback_error:
                        logger.error(f"Failed to fetch quote for {symbol} even with fallback: {fallback_error}")
                        # Skip this symbol
                        continue
            
            return quotes
        except Exception as e:
            logger.error(f"Error in batch quote fetch: {e}")
            # Fallback to individual fetches
            quotes = {}
            for symbol in symbols:
                try:
                    quotes[symbol] = self.get_quote(symbol)
                except Exception as individual_error:
                    logger.warning(f"Failed to fetch quote for {symbol}: {individual_error}")
                    continue
            return quotes

    def get_historical_data(
        self, symbol: str, period: str = "1mo"
    ) -> Dict[str, Any]:
        """
        Get historical data for a symbol

        Args:
            symbol: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)

        Returns:
            Historical data dictionary
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)

            return {
                "symbol": symbol,
                "period": period,
                "data": hist.to_dict("index"),
                "columns": list(hist.columns),
            }
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            raise

    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get company information

        Args:
            symbol: Stock symbol

        Returns:
            Company information dictionary
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            return {
                "symbol": symbol,
                "name": info.get("longName"),
                "sector": info.get("sector"),
                "industry": info.get("industry"),
                "description": info.get("longBusinessSummary"),
                "employees": info.get("fullTimeEmployees"),
                "website": info.get("website"),
            }
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            raise

    def get_financials(self, symbol: str) -> Dict[str, Any]:
        """
        Get financial statements

        Args:
            symbol: Stock symbol

        Returns:
            Financial statements dictionary
        """
        try:
            ticker = yf.Ticker(symbol)

            return {
                "symbol": symbol,
                "income_statement": ticker.financials.to_dict(),
                "balance_sheet": ticker.balance_sheet.to_dict(),
                "cash_flow": ticker.cashflow.to_dict(),
            }
        except Exception as e:
            logger.error(f"Error fetching financials for {symbol}: {e}")
            raise
