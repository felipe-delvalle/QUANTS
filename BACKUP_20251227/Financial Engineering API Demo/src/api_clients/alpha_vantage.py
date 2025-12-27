"""
Alpha Vantage API Client
Provides access to real-time and historical stock market data
"""

import logging
from typing import Dict, Any, Optional
from .base_client import BaseAPIClient

logger = logging.getLogger(__name__)


class AlphaVantageClient(BaseAPIClient):
    """Client for Alpha Vantage API"""

    BASE_URL = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str, rate_limit: int = 5):
        """
        Initialize Alpha Vantage client

        Args:
            api_key: Alpha Vantage API key
            rate_limit: Requests per minute (free tier: 5)
        """
        super().__init__(
            api_key=api_key,
            base_url=self.BASE_URL,
            rate_limit=rate_limit,
        )

    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get real-time quote for a symbol

        Args:
            symbol: Stock symbol (e.g., 'AAPL')

        Returns:
            Quote data dictionary
        """
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "datatype": "json",
        }

        response = self._make_request("GET", "", params=params)
        
        if "Global Quote" in response:
            quote = response["Global Quote"]
            return {
                "symbol": quote.get("01. symbol"),
                "price": float(quote.get("05. price", 0)),
                "change": float(quote.get("09. change", 0)),
                "change_percent": quote.get("10. change percent", "0%"),
                "volume": int(quote.get("06. volume", 0)),
                "high": float(quote.get("03. high", 0)),
                "low": float(quote.get("04. low", 0)),
                "open": float(quote.get("02. open", 0)),
                "previous_close": float(quote.get("08. previous close", 0)),
            }
        
        raise ValueError(f"Invalid response for {symbol}: {response}")

    def get_historical_data(
        self, symbol: str, period: str = "1mo"
    ) -> Dict[str, Any]:
        """
        Get historical data for a symbol

        Args:
            symbol: Stock symbol
            period: Time period (1mo, 3mo, 6mo, 1y, 2y, 5y, max)

        Returns:
            Historical data dictionary
        """
        period_map = {
            "1mo": "TIME_SERIES_DAILY",
            "3mo": "TIME_SERIES_DAILY",
            "6mo": "TIME_SERIES_DAILY",
            "1y": "TIME_SERIES_DAILY",
            "2y": "TIME_SERIES_WEEKLY",
            "5y": "TIME_SERIES_WEEKLY",
            "max": "TIME_SERIES_MONTHLY",
        }

        function = period_map.get(period, "TIME_SERIES_DAILY")
        params = {
            "function": function,
            "symbol": symbol,
            "outputsize": "full" if period in ["2y", "5y", "max"] else "compact",
            "datatype": "json",
        }

        response = self._make_request("GET", "", params=params)
        
        # Extract time series data
        time_series_key = None
        for key in response.keys():
            if "Time Series" in key:
                time_series_key = key
                break

        if not time_series_key:
            raise ValueError(f"No time series data found for {symbol}")

        return {
            "symbol": symbol,
            "metadata": response.get("Meta Data", {}),
            "time_series": response.get(time_series_key, {}),
        }

    def get_technical_indicator(
        self, symbol: str, indicator: str, interval: str = "daily"
    ) -> Dict[str, Any]:
        """
        Get technical indicator data

        Args:
            symbol: Stock symbol
            indicator: Indicator name (RSI, MACD, SMA, etc.)
            interval: Time interval (daily, weekly, monthly)

        Returns:
            Technical indicator data
        """
        params = {
            "function": indicator.upper(),
            "symbol": symbol,
            "interval": interval,
            "datatype": "json",
        }

        return self._make_request("GET", "", params=params)

    def search_symbols(self, keywords: str) -> Dict[str, Any]:
        """
        Search for symbols by keywords

        Args:
            keywords: Search keywords

        Returns:
            Search results
        """
        params = {
            "function": "SYMBOL_SEARCH",
            "keywords": keywords,
            "datatype": "json",
        }

        return self._make_request("GET", "", params=params)
