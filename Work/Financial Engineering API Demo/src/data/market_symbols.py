"""
Market Symbols
Defines market symbols organized by sector and asset type
"""

from enum import Enum
from typing import Dict, List

# GICS Sectors
class Sector(Enum):
    """GICS Sector enumeration"""
    INFORMATION_TECHNOLOGY = "Information Technology"
    HEALTH_CARE = "Health Care"
    FINANCIALS = "Financials"
    CONSUMER_DISCRETIONARY = "Consumer Discretionary"
    COMMUNICATION_SERVICES = "Communication Services"
    INDUSTRIALS = "Industrials"
    CONSUMER_STAPLES = "Consumer Staples"
    ENERGY = "Energy"
    UTILITIES = "Utilities"
    REAL_ESTATE = "Real Estate"
    MATERIALS = "Materials"


# Stock symbols by sector
MARKET_SYMBOLS: Dict[Sector, List[str]] = {
    Sector.INFORMATION_TECHNOLOGY: [
        "AAPL", "MSFT", "GOOGL", "GOOG", "AMZN", "NVDA", "META", "TSLA",
        "ORCL", "CRM", "ADBE", "INTC", "CSCO", "IBM", "AMD", "QCOM"
    ],
    Sector.HEALTH_CARE: [
        "JNJ", "UNH", "PFE", "ABBV", "TMO", "ABT", "DHR", "BMY",
        "AMGN", "GILD", "CVS", "CI", "HUM", "ELV", "BSX", "ZTS"
    ],
    Sector.FINANCIALS: [
        "JPM", "BAC", "WFC", "GS", "MS", "C", "BLK", "SCHW",
        "AXP", "COF", "USB", "PNC", "TFC", "BK", "STT", "MTB"
    ],
    Sector.CONSUMER_DISCRETIONARY: [
        "AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "LOW", "TJX",
        "BKNG", "NFLX", "CMCSA", "DIS", "TGT", "GM", "F", "EBAY"
    ],
    Sector.COMMUNICATION_SERVICES: [
        "META", "GOOGL", "GOOG", "NFLX", "DIS", "CMCSA", "VZ", "T",
        "CHTR", "TMUS", "EA", "TTWO", "LYFT", "UBER", "SNAP"
    ],
    Sector.INDUSTRIALS: [
        "BA", "CAT", "GE", "HON", "UPS", "RTX", "LMT", "DE",
        "EMR", "ETN", "ITW", "PH", "CMI", "FTV", "TDG", "AME"
    ],
    Sector.CONSUMER_STAPLES: [
        "WMT", "PG", "KO", "PEP", "COST", "PM", "MO", "CL",
        "MDLZ", "STZ", "TGT", "KR", "SYY", "ADM", "BG", "TSN"
    ],
    Sector.ENERGY: [
        "XOM", "CVX", "SLB", "EOG", "COP", "MPC", "VLO", "PSX",
        "OXY", "HAL", "FANG", "DVN", "CTRA", "MRO", "APA", "OVV"
    ],
    Sector.UTILITIES: [
        "NEE", "DUK", "SO", "D", "AEP", "SRE", "EXC", "XEL",
        "WEC", "ES", "PEG", "ED", "EIX", "FE", "ETR", "AEE"
    ],
    Sector.REAL_ESTATE: [
        "AMT", "PLD", "EQIX", "PSA", "WELL", "SPG", "O", "DLR",
        "VICI", "EXPI", "CBRE", "CUBE", "AVB", "EQR", "UDR", "MAA"
    ],
    Sector.MATERIALS: [
        "LIN", "APD", "SHW", "ECL", "DD", "PPG", "FCX", "NEM",
        "VALE", "RIO", "BHP", "NUE", "STLD", "CLF", "CMC"
    ],
}

# Crypto symbols
CRYPTO_SYMBOLS: List[str] = [
    "BTC-USD", "ETH-USD", "SOL-USD", "ADA-USD", "DOT-USD", "AVAX-USD",
    "LINK-USD", "LTC-USD", "ATOM-USD", "ETC-USD", "XLM-USD", "XRP-USD",
    "DOGE-USD", "MATIC-USD"
]

# Forex pairs
FOREX_PAIRS: List[str] = [
    "EURUSD=X", "GBPUSD=X", "USDJPY=X", "USDCHF=X", "AUDUSD=X", "USDCAD=X",
    "NZDUSD=X", "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDJPY=X", "EURCHF=X"
]

# Commodities
COMMODITIES: List[str] = [
    "GC=F", "SI=F", "PL=F", "PA=F",  # Metals: Gold, Silver, Platinum, Palladium
    "CL=F", "NG=F", "HG=F",          # Energy/Metals: Crude, Nat Gas, Copper
    "ZC=F", "ZW=F", "ZS=F",          # Ags: Corn, Wheat, Soybeans
    "SB=F", "KC=F"                   # Softs: Sugar, Coffee
]
