"""
Unified data loader with caching and retry support across asset classes.
"""

import logging
import time
from typing import Optional, Dict, Any

from cachetools import TTLCache
from ..config import AssetType, DEFAULT_MAX_RETRIES, DEFAULT_BACKOFF_SECONDS, get_settings
from ..api_clients.yahoo_finance import YahooFinanceClient
from ..api_clients.crypto_client import CryptoClient
from ..api_clients.forex_client import ForexClient
from ..api_clients.metals_client import MetalsClient

try:
    import pandas as pd
except ImportError:
    pd = None  # type: ignore

from ..utils.cache_manager import get_cache_manager, cache_result

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Fetches and caches OHLCV/quote data with retry logic.
    """

    def __init__(
        self,
        cache_ttl_seconds: int = 900,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_seconds: float = DEFAULT_BACKOFF_SECONDS,
    ) -> None:
        self.settings = get_settings()
        self.cache = TTLCache(maxsize=256, ttl=cache_ttl_seconds)
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds
        self.stock_client = YahooFinanceClient()
        self.crypto_client = CryptoClient()
        self.forex_client = ForexClient()
        self.metals_client = MetalsClient()

    def get_ohlcv(self, symbol: str, asset_type: str, period: str = "6mo") -> Optional[pd.DataFrame]:
        """
        Retrieve OHLCV data for any supported asset.
        """
        cache_key = f"{asset_type}:{symbol}:{period}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        for attempt in range(1, self.max_retries + 1):
            try:
                df = self._fetch(symbol, asset_type, period)
                if df is not None:
                    self.cache[cache_key] = df
                return df
            except Exception as exc:
                logger.warning(
                    "Data fetch failed (%s attempt %s/%s): %s",
                    symbol,
                    attempt,
                    self.max_retries,
                    exc,
                )
                if attempt == self.max_retries:
                    return None
                time.sleep(self.backoff_seconds * attempt)
        return None

    def _fetch(self, symbol: str, asset_type: str, period: str):
        if pd is None:
            raise ImportError("pandas is required for data loading")

        asset = AssetType(asset_type)

        if asset == AssetType.STOCK:
            data = self.stock_client.get_historical_data(symbol, period=period)
        elif asset == AssetType.CRYPTO:
            data = self.crypto_client.get_historical_data(symbol, period=period)
        elif asset == AssetType.FOREX:
            data = self.forex_client.get_historical_data(symbol, period=period)
        elif asset == AssetType.METAL:
            data = self.metals_client.get_historical_data(symbol, period=period)
        else:
            raise ValueError(f"Unsupported asset type: {asset_type}")

        # Handle empty data
        if not data.get("data") or len(data["data"]) == 0:
            logger.warning(f"No data returned for {symbol} ({asset_type})")
            return None
        
        df = pd.DataFrame(data["data"]).T
        if len(df) == 0:
            logger.warning(f"Empty DataFrame for {symbol} ({asset_type})")
            return None
            
        df.index = pd.to_datetime(df.index)
        
        # Normalize column names (handle both capitalized and lowercase)
        column_mapping = {}
        for old_name, new_name in [
            ("Open", "open"), ("High", "high"), ("Low", "low"), 
            ("Close", "close"), ("Volume", "volume"),
            ("open", "open"), ("high", "high"), ("low", "low"),
            ("close", "close"), ("volume", "volume")
        ]:
            if old_name in df.columns:
                column_mapping[old_name] = new_name
        
        if not column_mapping:
            logger.error(f"No recognized columns in DataFrame for {symbol}. Columns: {list(df.columns)}")
            return None
            
        df.rename(columns=column_mapping, inplace=True)
        
        # Ensure required columns exist
        required_cols = ["open", "high", "low", "close", "volume"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            logger.error(f"Missing required columns for {symbol}: {missing_cols}")
            return None
            
        return df[required_cols]
