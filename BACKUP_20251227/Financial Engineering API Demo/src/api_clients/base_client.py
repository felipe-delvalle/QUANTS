"""
Base API Client
Provides common functionality for all API clients
"""

import time
import requests
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from cachetools import TTLCache
import logging

logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """Base class for all API clients with common functionality"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        rate_limit: int = 5,
        timeout: int = 30,
        cache_ttl: int = 3600,
    ):
        """
        Initialize base API client

        Args:
            api_key: API key for authentication
            base_url: Base URL for API requests
            rate_limit: Requests per second limit
            timeout: Request timeout in seconds
            cache_ttl: Cache time-to-live in seconds
        """
        self.api_key = api_key
        self.base_url = base_url
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.cache = TTLCache(maxsize=100, ttl=cache_ttl)
        self.last_request_time = 0
        self.session = requests.Session()

    def _rate_limit(self):
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        min_interval = 1.0 / self.rate_limit

        if time_since_last < min_interval:
            sleep_time = min_interval - time_since_last
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _get_cache_key(self, endpoint: str, params: Dict) -> str:
        """Generate cache key from endpoint and parameters"""
        return f"{endpoint}:{hash(frozenset(params.items()))}"

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Make HTTP request with rate limiting and caching

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Request parameters
            use_cache: Whether to use cache

        Returns:
            Response data as dictionary
        """
        params = params or {}
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        # Check cache
        if use_cache and method == "GET":
            cache_key = self._get_cache_key(endpoint, params)
            if cache_key in self.cache:
                logger.info(f"Cache hit for {endpoint}")
                return self.cache[cache_key]

        # Rate limiting
        self._rate_limit()

        # Add authentication
        headers = self._get_headers()
        if self.api_key:
            params = self._add_auth(params)

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params if method == "GET" else None,
                json=params if method in ["POST", "PUT", "PATCH"] else None,
                headers=headers,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            # Cache successful GET requests
            if use_cache and method == "GET":
                self.cache[cache_key] = data

            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise

    def _get_headers(self) -> Dict[str, str]:
        """Get default headers"""
        return {
            "Content-Type": "application/json",
            "User-Agent": "Financial-Engineering-API-Demo/1.0",
        }

    def _add_auth(self, params: Dict) -> Dict:
        """Add authentication to parameters"""
        if self.api_key:
            params["apikey"] = self.api_key
        return params

    @abstractmethod
    def get_quote(self, symbol: str) -> Dict[str, Any]:
        """Get current quote for a symbol"""
        pass

    @abstractmethod
    def get_historical_data(
        self, symbol: str, period: str = "1mo"
    ) -> Dict[str, Any]:
        """Get historical data for a symbol"""
        pass
