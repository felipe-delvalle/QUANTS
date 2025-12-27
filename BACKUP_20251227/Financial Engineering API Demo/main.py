#!/usr/bin/env python3
"""
Financial Engineering API Demo - Main Entry Point
Demonstrates multi-API integration and portfolio analysis
"""

import os
import sys
import logging
from dotenv import load_dotenv
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from api_clients.alpha_vantage import AlphaVantageClient
from api_clients.yahoo_finance import YahooFinanceClient
from api_clients.github_api import GitHubAPIClient
from analysis.portfolio import PortfolioAnalyzer
from orchestrator.workflow import WorkflowOrchestrator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def demo_alpha_vantage():
    """Demonstrate Alpha Vantage API"""
    logger.info("=== Alpha Vantage API Demo ===")
    
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        logger.warning("ALPHA_VANTAGE_API_KEY not set, skipping demo")
        return

    client = AlphaVantageClient(api_key=api_key)
    
    # Get quote
    try:
        quote = client.get_quote("AAPL")
        logger.info(f"AAPL Quote: {quote}")
    except Exception as e:
        logger.error(f"Error fetching quote: {e}")


def demo_yahoo_finance():
    """Demonstrate Yahoo Finance API"""
    logger.info("=== Yahoo Finance API Demo ===")
    
    client = YahooFinanceClient()
    
    # Get quote
    try:
        quote = client.get_quote("AAPL")
        logger.info(f"AAPL Quote: {quote}")
        
        # Get company info
        info = client.get_company_info("AAPL")
        logger.info(f"AAPL Company Info: {info}")
    except Exception as e:
        logger.error(f"Error: {e}")


def demo_github_api():
    """Demonstrate GitHub API"""
    logger.info("=== GitHub API Demo ===")
    
    try:
        from api_clients.github_api import GitHubAPIClient
    except ImportError as e:
        logger.warning(f"GitHub API not available: {e}")
        return
    
    token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPO")
    
    if not token or not repo:
        logger.warning("GITHUB_TOKEN or GITHUB_REPO not set, skipping demo")
        return

    try:
        client = GitHubAPIClient(token=token)
        
        # Get repository info
        repo_info = client.get_repository_info(repo)
        logger.info(f"Repository Info: {repo_info}")
        
        # Get recent commits
        commits = client.get_commits(repo, limit=5)
        logger.info(f"Recent Commits: {len(commits)} commits found")
    except Exception as e:
        logger.error(f"Error: {e}")


def demo_portfolio_analysis():
    """Demonstrate portfolio analysis"""
    logger.info("=== Portfolio Analysis Demo ===")
    
    # This would typically fetch real data from APIs
    # For demo, we'll use sample data
    import pandas as pd
    import numpy as np
    
    dates = pd.date_range(start="2024-01-01", end="2024-12-01", freq="D")
    np.random.seed(42)
    
    # Generate sample price data
    prices = pd.DataFrame({
        "AAPL": 150 + np.cumsum(np.random.randn(len(dates)) * 2),
        "GOOGL": 140 + np.cumsum(np.random.randn(len(dates)) * 2),
        "MSFT": 380 + np.cumsum(np.random.randn(len(dates)) * 2),
    }, index=dates)
    
    # Analyze portfolio
    portfolio = PortfolioAnalyzer(symbols=["AAPL", "GOOGL", "MSFT"])
    analysis = portfolio.analyze_portfolio(prices)
    
    logger.info(f"Portfolio Analysis Results:")
    logger.info(f"  Annual Return: {analysis['risk_metrics']['annual_return']:.2%}")
    logger.info(f"  Sharpe Ratio: {analysis['risk_metrics']['sharpe_ratio']:.2f}")
    logger.info(f"  Max Drawdown: {analysis['risk_metrics']['max_drawdown']:.2%}")


def demo_workflow():
    """Demonstrate workflow orchestration"""
    logger.info("=== Workflow Orchestration Demo ===")
    
    orchestrator = WorkflowOrchestrator()
    
    try:
        results = orchestrator.run_analysis_workflow(
            symbols=["AAPL", "GOOGL"],
            risk_level="moderate"
        )
        logger.info(f"Workflow Results: {results}")
    except Exception as e:
        logger.error(f"Error in workflow: {e}")


def main():
    """Main function"""
    logger.info("Financial Engineering API Demo Starting...")
    logger.info("=" * 50)
    
    # Run demos
    demo_yahoo_finance()
    demo_alpha_vantage()
    demo_github_api()
    demo_portfolio_analysis()
    demo_workflow()
    
    logger.info("=" * 50)
    logger.info("Demo completed!")


if __name__ == "__main__":
    main()
