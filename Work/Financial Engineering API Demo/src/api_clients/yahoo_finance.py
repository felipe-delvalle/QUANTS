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

from typing import Dict, Any, Optional
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
