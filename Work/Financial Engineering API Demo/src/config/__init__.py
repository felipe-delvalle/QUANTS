"""
Configuration Module
Provides settings and configuration utilities
"""

import os
import logging
from enum import Enum
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Default retry configuration constants
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_SECONDS = 1.0


class AssetType(Enum):
    """Asset type enumeration"""
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"
    METAL = "commodities"


@dataclass
class Settings:
    """Application settings"""
    log_level: str = "INFO"
    github_token: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    yahoo_finance_enabled: bool = True
    fred_api_key: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables"""
        return cls(
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            github_token=os.getenv("GITHUB_TOKEN"),
            alpha_vantage_api_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
            yahoo_finance_enabled=os.getenv("YAHOO_FINANCE_ENABLED", "true").lower() == "true",
            fred_api_key=os.getenv("FRED_API_KEY"),
        )


def get_settings() -> Settings:
    """
    Get application settings
    
    Returns:
        Settings object with configuration values
    """
    return Settings.from_env()


def configure_logging(log_level: str, name: str) -> logging.Logger:
    """
    Configure and return a logger
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging if not already configured
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=numeric_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    return logging.getLogger(name)


__all__ = [
    "get_settings",
    "configure_logging",
    "AssetType",
    "Settings",
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_BACKOFF_SECONDS",
]

