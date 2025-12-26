"""
API Clients Module
Handles all external API integrations
"""

from .base_client import BaseAPIClient
from .alpha_vantage import AlphaVantageClient
from .yahoo_finance import YahooFinanceClient
from .github_api import GitHubAPIClient

try:
    from .teams_planner import TeamsPlannerClient
    TEAMS_PLANNER_AVAILABLE = True
except ImportError:
    TEAMS_PLANNER_AVAILABLE = False
    TeamsPlannerClient = None

__all__ = [
    "BaseAPIClient",
    "AlphaVantageClient",
    "YahooFinanceClient",
    "GitHubAPIClient",
]

if TEAMS_PLANNER_AVAILABLE:
    __all__.append("TeamsPlannerClient")
