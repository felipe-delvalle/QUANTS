#!/usr/bin/env python3
"""
CLI Interface for Financial Engineering API Demo
"""

import argparse
import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from api_clients.yahoo_finance import YahooFinanceClient
from api_clients.alpha_vantage import AlphaVantageClient
from api_clients.github_api import GitHubAPIClient

load_dotenv()


def get_quote(args):
    """Get stock quote"""
    if args.source == "yahoo":
        client = YahooFinanceClient()
    elif args.source == "alpha":
        api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
        if not api_key:
            print("Error: ALPHA_VANTAGE_API_KEY not set")
            return
        client = AlphaVantageClient(api_key=api_key)
    else:
        print("Invalid source. Use 'yahoo' or 'alpha'")
        return

    quote = client.get_quote(args.symbol)
    print(f"\n{args.symbol} Quote:")
    print(f"  Price: ${quote['price']:.2f}")
    print(f"  Change: ${quote['change']:.2f} ({quote.get('change_percent', 'N/A')})")
    print(f"  Volume: {quote['volume']:,}")


def main():
    parser = argparse.ArgumentParser(
        description="Financial Engineering API Demo CLI"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Quote command
    quote_parser = subparsers.add_parser("quote", help="Get stock quote")
    quote_parser.add_argument("symbol", help="Stock symbol")
    quote_parser.add_argument(
        "--source",
        choices=["yahoo", "alpha"],
        default="yahoo",
        help="Data source",
    )
    quote_parser.set_defaults(func=get_quote)

    args = parser.parse_args()

    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
