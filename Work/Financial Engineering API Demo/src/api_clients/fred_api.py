"""
FRED API Client
Fetches US Treasury yield data from Federal Reserve Economic Data (FRED)
"""

import requests
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from cachetools import TTLCache

logger = logging.getLogger(__name__)

# FRED Treasury Constant Maturity Rate series IDs
# Mapping: series_id -> (tenor_years, display_name)
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

# Cache for 1 hour (Treasury data updates daily)
_yield_cache = TTLCache(maxsize=10, ttl=3600)


class FREDClient:
    """Client for FRED API to fetch Treasury yield data"""

    BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize FRED client

        Args:
            api_key: FRED API key (get free key from https://fred.stlouisfed.org/docs/api/api_key.html)
        """
        self.api_key = api_key
        if not api_key:
            logger.warning("FRED API key not provided. Real market data will not be available.")

    def _fetch_series_latest(self, series_id: str) -> Optional[float]:
        """
        Fetch the latest observation for a FRED series

        Args:
            series_id: FRED series ID (e.g., 'DGS10')

        Returns:
            Latest rate value or None if unavailable
        """
        if not self.api_key:
            return None

        cache_key = f"fred_{series_id}_latest"
        if cache_key in _yield_cache:
            return _yield_cache[cache_key]

        try:
            # FRED API v2 format - according to official docs at https://fred.stlouisfed.org/docs/api/fred/
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "limit": 1,  # Only get latest observation (fast!)
                "sort_order": "desc",  # Most recent first
            }

            response = requests.get(self.BASE_URL, params=params, timeout=10)
            
            # Check for API errors first
            if response.status_code != 200:
                error_data = response.text
                logger.error(f"FRED API error for {series_id}: {response.status_code} - {error_data}")
                # Try to parse JSON error if available
                try:
                    error_json = response.json()
                    if "error_message" in error_json:
                        logger.error(f"FRED API error message: {error_json['error_message']}")
                except:
                    pass
                return None
            
            data = response.json()

            # FRED API response structure: {"observations": [...]}
            if "observations" in data and len(data["observations"]) > 0:
                obs = data["observations"][0]
                value_str = obs.get("value", ".")
                if value_str != "." and value_str is not None:  # FRED uses "." for missing data
                    try:
                        rate = float(value_str) / 100.0  # Convert percentage to decimal
                        _yield_cache[cache_key] = rate
                        return rate
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid value format for {series_id}: {value_str}")
                        return None

            logger.warning(f"No valid data for series {series_id}")
            return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Network error fetching FRED series {series_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error fetching FRED series {series_id}: {e}", exc_info=True)
            return None

    def fetch_treasury_yields(self) -> Tuple[List[float], List[float]]:
        """
        Fetch current US Treasury yields for all available maturities

        Returns:
            Tuple of (tenors, rates) where:
            - tenors: List of tenor values in years
            - rates: List of corresponding rates (as decimals, e.g., 0.05 for 5%)
        """
        if not self.api_key:
            raise ValueError("FRED API key required. Get a free key from https://fred.stlouisfed.org/docs/api/api_key.html")

        # Check cache first
        cache_key = "treasury_yields_full"
        if cache_key in _yield_cache:
            return _yield_cache[cache_key]

        # Fetch all series in parallel for speed
        tenors = []
        rates = []
        series_list = list(TREASURY_SERIES.keys())

        # Use ThreadPoolExecutor for parallel requests (much faster!)
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

        # Build sorted list of tenors and rates
        for series_id in sorted(series_list, key=lambda x: TREASURY_SERIES[x][0]):
            if series_id in results:
                tenor, _ = TREASURY_SERIES[series_id]
                tenors.append(tenor)
                rates.append(results[series_id])

        if not tenors:
            raise ValueError("No Treasury yield data available from FRED")

        # Cache the result
        result = (tenors, rates)
        _yield_cache[cache_key] = result
        return result

    def get_yield_curve_data(self) -> Dict:
        """
        Get yield curve data formatted for the UI

        Returns:
            Dictionary with tenors, rates, and metadata
        """
        tenors, rates = self.fetch_treasury_yields()
        return {
            "tenors": tenors,
            "rates": [r * 100 for r in rates],  # Convert to percentage for display
            "source": "FRED (Federal Reserve Economic Data)",
            "as_of": datetime.now().isoformat(),
            "is_real_data": True,
        }

