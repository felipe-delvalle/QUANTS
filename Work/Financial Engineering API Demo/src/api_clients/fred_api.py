"""
FRED API Client for fetching US Treasury yields
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# Treasury series IDs and their tenors
TREASURY_SERIES = {
    "DGS1MO": (1/12, "1 Month"),
    "DGS3MO": (0.25, "3 Month"),
    "DGS6MO": (0.5, "6 Month"),
    "DGS1": (1.0, "1 Year"),
    "DGS2": (2.0, "2 Year"),
    "DGS3": (3.0, "3 Year"),
    "DGS5": (5.0, "5 Year"),
    "DGS7": (7.0, "7 Year"),
    "DGS10": (10.0, "10 Year"),
    "DGS20": (20.0, "20 Year"),
    "DGS30": (30.0, "30 Year"),
}

# Cache for 1 hour
_yield_cache: TTLCache = TTLCache(maxsize=10, ttl=3600)


class FREDClient:
    """Client for fetching data from FRED (Federal Reserve Economic Data)"""
    
    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        if not api_key:
            logger.warning("FRED API key not provided. Real market data will not be available.")

    def _fetch_series_latest(self, series_id: str) -> Optional[float]:
        """Fetch the latest value for a FRED series."""
        if not self.api_key:
            return None

        cache_key = f"fred_{series_id}_latest"
        if cache_key in _yield_cache:
            return _yield_cache[cache_key]

        try:
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "limit": 1,
                "sort_order": "desc",
            }
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if "observations" in data and len(data["observations"]) > 0:
                obs = data["observations"][0]
                value_str = obs.get("value", ".")
                if value_str != ".":
                    rate = float(value_str)  # Rate is already in percentage form
                    _yield_cache[cache_key] = rate
                    return rate

            logger.warning(f"No valid data for series {series_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {e}")
            return None

    def fetch_treasury_yields(self) -> Tuple[List[float], List[float]]:
        """Fetch all Treasury yields in parallel."""
        if not self.api_key:
            raise ValueError("FRED API key required. Get a free key from https://fred.stlouisfed.org/docs/api/api_key.html")

        cache_key = "treasury_yields_full"
        if cache_key in _yield_cache:
            return _yield_cache[cache_key]

        tenors: List[float] = []
        rates: List[float] = []
        series_list = list(TREASURY_SERIES.keys())

        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_series = {
                executor.submit(self._fetch_series_latest, series_id): series_id
                for series_id in series_list
            }
            results = {}
            for future in as_completed(future_to_series):
                series_id = future_to_series[future]
                try:
                    rate = future.result()
                    if rate is not None:
                        results[series_id] = rate
                except Exception as e:
                    logger.error(f"Error fetching {series_id}: {e}")

        # Sort by tenor
        for series_id in sorted(series_list, key=lambda x: TREASURY_SERIES[x][0]):
            if series_id in results:
                tenor, _ = TREASURY_SERIES[series_id]
                tenors.append(tenor)
                rates.append(results[series_id])

        if not tenors:
            raise ValueError("No Treasury yield data available from FRED")

        result = (tenors, rates)
        _yield_cache[cache_key] = result
        return result

    def get_yield_curve_data(self) -> Dict:
        """Get yield curve data in a format ready for the API."""
        tenors, rates = self.fetch_treasury_yields()
        return {
            "tenors": tenors,
            "rates": rates,  # Already in percentage form
            "source": "FRED (Federal Reserve Economic Data)",
            "as_of": datetime.now().isoformat(),
            "is_real_data": True,
        }

