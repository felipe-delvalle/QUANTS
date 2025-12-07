"""
FastAPI service exposing scan, signal, and backtest endpoints.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import json
from typing import List, Optional, Dict
import os
from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException, Header, Request, Query
from pydantic import BaseModel
from cachetools import TTLCache
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.config import get_settings, configure_logging, AssetType
from src.data import DataLoader
from src.trading.market_scanner import MarketScanner
from src.trading.signal_generator import SignalGenerator
from src.data.market_symbols import Sector, MARKET_SYMBOLS, CRYPTO_SYMBOLS, FOREX_PAIRS, COMMODITIES
from src.data.historical_fetcher import HistoricalFetcher
from src.analysis import DetailedAnalyzer, ReportGenerator
from src.analysis.advanced_indicators import AdvancedIndicators
from src.backtesting import BacktestEngine

settings = get_settings()
logger = configure_logging(settings.log_level, __name__)

app = FastAPI(title="Premium Trading API", version="1.0.0")
templates = Jinja2Templates(directory="templates")

# Ensure output directory exists for PDF reports
output_dir = project_root / "output"
output_dir.mkdir(exist_ok=True)

app.mount("/output", StaticFiles(directory=str(output_dir)), name="output")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Simple in-memory rate limiting
rate_limiter = TTLCache(maxsize=512, ttl=60)

# Dashboard result caching (5 minute TTL)
dashboard_cache = TTLCache(maxsize=128, ttl=300)


def _get_dashboard_cache_key(threshold: float, sectors: Optional[str], asset_types: Optional[str], demo: bool) -> str:
    """Generate cache key for dashboard results"""
    sectors_str = sectors or "all"
    asset_types_str = asset_types or "none"
    return f"dashboard:{threshold:.2f}:{sectors_str}:{asset_types_str}:{demo}"



def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if settings.github_token:  # reuse as API token placeholder
        if x_api_key != settings.github_token:
            raise HTTPException(status_code=401, detail="Invalid API key")
    return True


def check_rate_limit(client_id: str):
    hits = rate_limiter.get(client_id, 0)
    if hits > 30:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    rate_limiter[client_id] = hits + 1


class ScanRequest(BaseModel):
    symbols: List[str]
    asset_type: AssetType = AssetType.STOCK
    min_confidence: float = 0.6
    strategy: str = "comprehensive"
    period: str = "6mo"


class BacktestRequest(BaseModel):
    prices: List[float]
    signals: Optional[List[float]] = None
    fee_bps: float = 5.0
    slippage_bps: float = 5.0


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/scan")
def scan(req: ScanRequest, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    check_rate_limit("scan")

    loader = DataLoader()
    scanner = MarketScanner(data_loader=loader)
    opps = scanner.scan_stocks(
        req.symbols,
        min_confidence=req.min_confidence,
        strategy=req.strategy,
        asset_type=req.asset_type.value,
        period=req.period,
    )
    return {"count": len(opps), "opportunities": opps}


@app.post("/backtest")
def backtest(req: BacktestRequest, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    check_rate_limit("backtest")

    engine = BacktestEngine(fee_bps=req.fee_bps, slippage_bps=req.slippage_bps)
    import pandas as pd

    price_series = pd.Series(req.prices)
    if req.signals:
        signals = pd.Series(req.signals, index=price_series.index)
    else:
        # default: simple moving average crossover proxy
        signals = (price_series > price_series.rolling(20).mean()).astype(int)

    result = engine.backtest_signals(price_series, signals)
    return {
        "metrics": result.metrics,
        "equity_curve": result.equity_curve.tolist(),
        "returns": result.returns.tolist(),
    }


@app.get("/")
def root():
    return RedirectResponse(url="/home", status_code=307)


@app.get("/home", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "title": "FDV-QUANTS",
            "endpoints": [
                {"method": "GET", "path": "/home", "desc": "Home - navigation"},
                {"method": "GET", "path": "/dashboard", "desc": "Trading opportunities dashboard"},
                {"method": "GET", "path": "/gallery", "desc": "Chart gallery"},
                {"method": "GET", "path": "/health", "desc": "Health check"},
                {"method": "GET", "path": "/", "desc": "API root"},
                {"method": "POST", "path": "/scan", "desc": "Scan for trading opportunities (requires API key)"},
                {"method": "POST", "path": "/backtest", "desc": "Backtest strategies (requires API key)"},
            ],
        },
    )


def _categorize_opportunities(opportunities: List[Dict]) -> Dict[str, List[Dict]]:
    """
    Categorize opportunities into 'On Sale' (undervalued) and 'Overbought' (overvalued).
    
    Args:
        opportunities: List of opportunity dictionaries
        
    Returns:
        Dictionary with 'on_sale' and 'overbought' lists
    """
    on_sale = []
    overbought = []
    
    undervalued_keywords = [
        "oversold", "lower", "support", "below", "buy", "bullish",
        "at lower", "RSI oversold", "Price at lower"
    ]
    
    overbought_keywords = [
        "overbought", "upper", "resistance", "above", "sell", "bearish",
        "at upper", "RSI overbought", "Price at upper"
    ]
    
    for opp in opportunities:
        reasons = " ".join(opp.get("reasons", [])).lower()
        signal = opp.get("signal", "").upper()
        
        # Check for undervalued indicators
        is_undervalued = any(keyword in reasons for keyword in undervalued_keywords) or signal == "BUY"
        
        # Check for overbought indicators  
        is_overvalued = any(keyword in reasons for keyword in overbought_keywords) or signal == "SELL"
        
        # Categorize based on RSI if available
        rsi_match = None
        for reason in opp.get("reasons", []):
            if "RSI" in reason:
                if "oversold" in reason.lower():
                    is_undervalued = True
                    rsi_match = "oversold"
                elif "overbought" in reason.lower():
                    is_overvalued = True
                    rsi_match = "overbought"
                break
        
        # Prioritize RSI-based categorization
        if rsi_match == "oversold":
            on_sale.append(opp)
        elif rsi_match == "overbought":
            overbought.append(opp)
        elif is_undervalued and not is_overvalued:
            on_sale.append(opp)
        elif is_overvalued and not is_undervalued:
            overbought.append(opp)
        # If both or neither, use signal type
        elif signal == "BUY":
            on_sale.append(opp)
        elif signal == "SELL":
            overbought.append(opp)
    
    return {
        "on_sale": on_sale,
        "overbought": overbought
    }


def _get_asset_type(symbol: str) -> AssetType:
    """Map symbol to its asset type."""
    symbol_upper = symbol.upper()
    
    # Known crypto symbols
    crypto_symbols = {"BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", "MATIC", "AVAX", "LINK", "UNI", "LTC", "ATOM", "ETC"}
    if symbol_upper in crypto_symbols:
        return AssetType.CRYPTO
    
    # Known forex pairs
    forex_pairs = {"EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD", "NZDUSD", "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "EURCHF", "USDMXN", "USDCNH", "USDINR"}
    if symbol_upper in forex_pairs:
        return AssetType.FOREX
    
    # Known metals
    metals = {"GOLD", "SILVER", "PLATINUM", "PALLADIUM"}
    if symbol_upper in metals:
        return AssetType.METAL
    
    # Default to stock
    return AssetType.STOCK



# API Endpoints

@app.get("/api/symbols")
def get_symbols(sector: Optional[str] = None, asset_type: Optional[str] = None):
    """
    Get available symbols, optionally filtered by sector or asset type
    
    Args:
        sector: GICS sector name (e.g., "Information Technology")
        asset_type: Asset type (stock, crypto, forex, commodities)
    """
    result = {
        "total": 0,
        "symbols": []
    }
    
    if sector:
        # Get symbols for specific sector
        for sec in Sector:
            if sec.value == sector:
                result["symbols"] = MARKET_SYMBOLS.get(sec, [])
                result["total"] = len(result["symbols"])
                break
    elif asset_type:
        # Get symbols by asset type
        if asset_type.lower() == "crypto":
            result["symbols"] = CRYPTO_SYMBOLS
        elif asset_type.lower() == "forex":
            result["symbols"] = FOREX_PAIRS
        elif asset_type.lower() == "commodities":
            result["symbols"] = COMMODITIES
        else:  # stocks - return all
            all_stocks = []
            for symbols in MARKET_SYMBOLS.values():
                all_stocks.extend(symbols)
            result["symbols"] = all_stocks
        result["total"] = len(result["symbols"])
    else:
        # Return all symbols organized by type
        result = {
            "stocks": {
                sector.value: symbols for sector, symbols in MARKET_SYMBOLS.items()
            },
            "crypto": CRYPTO_SYMBOLS,
            "forex": FOREX_PAIRS,
            "commodities": COMMODITIES
        }
    
    return result


@app.get("/api/analysis/{symbol}")
def get_detailed_analysis(symbol: str, signal_type: Optional[str] = None):
    """
    Get comprehensive analysis for a symbol
    
    Args:
        symbol: Stock/crypto/forex symbol
    """
    try:
        # Initialize components
        loader = DataLoader()
        analyzer = DetailedAnalyzer(loader)
        historical_fetcher = HistoricalFetcher()
        
        # Determine asset type
        asset_type = _get_asset_type(symbol)
        
        # Fetch historical data
        historical_data = historical_fetcher.fetch_historical_data(
            symbol, asset_type, years=1, use_cache=True
        )
        
        if historical_data is None or len(historical_data) < 50:
            raise HTTPException(status_code=404, detail=f"Insufficient data for {symbol}")
        
        # Get current price
        current_price = float(historical_data["close"].iloc[-1])
        
        # Generate comprehensive analysis
        analysis = analyzer.generate_comprehensive_analysis(
            symbol=symbol,
            current_price=current_price,
            historical_data=historical_data
        )
        
        # Add advanced indicators
        indicators = AdvancedIndicators()
        analysis["advanced_indicators"] = {
            "fdv_score": float(indicators.fdv_momentum_score(
                historical_data["close"],
                historical_data.get("volume")
            ).iloc[-1]),
            "smart_money_flow": float(indicators.smart_money_flow_index(
                historical_data["close"],
                historical_data["high"],
                historical_data["low"],
                historical_data["volume"]
            ).iloc[-1]) if "volume" in historical_data else 50.0
        }
        
        # Generate professional report excerpt
        report_gen = ReportGenerator()
        analysis["report_excerpt"] = report_gen._generate_executive_summary(symbol, analysis)
        
        return analysis
        
    except Exception as e:
        logger.error(f"Error generating analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/historical/{symbol}")
def get_historical_data(
    symbol: str,
    period: str = "1y",
    interval: str = "1d",
    indicators: bool = True
):
    """
    Get historical data with optional technical indicators
    
    Args:
        symbol: Stock/crypto/forex symbol
        period: Time period (1d, 1w, 1mo, 3mo, 6mo, 1y, 5y)
        interval: Data interval (1d, 1h, 5m)
        indicators: Include technical indicators
    """
    try:
        # Initialize fetcher
        fetcher = HistoricalFetcher()
        
        # Determine asset type
        asset_type = _get_asset_type(symbol)
        
        # Convert period to years
        period_map = {
            "1d": 0.003, "1w": 0.019, "1mo": 0.083,
            "3mo": 0.25, "6mo": 0.5, "1y": 1, "5y": 5
        }
        years = period_map.get(period, 1)
        
        # Fetch data
        data = fetcher.fetch_historical_data(symbol, asset_type, years=years)
        
        if data is None:
            raise HTTPException(status_code=404, detail=f"No data available for {symbol}")
        
        # Prepare response
        result = {
            "symbol": symbol,
            "period": period,
            "data_points": len(data),
            "prices": data[["open", "high", "low", "close", "volume"]].to_dict(orient="index")
        }
        
        # Add indicators if requested
        if indicators and len(data) > 50:
            from src.trading.technical_indicators import TechnicalAnalyzer
            
            analyzer = TechnicalAnalyzer(data["close"])
            analyzer.set_ohlcv(high=data["high"], low=data["low"], volume=data.get("volume"))
            
            analysis = analyzer.comprehensive_analysis()
            
            # Convert series to dict for JSON serialization
            result["indicators"] = {
                "sma_20": analysis["moving_averages"]["ma_20"].to_dict() if "ma_20" in analysis["moving_averages"] else {},
                "sma_50": analysis["moving_averages"]["ma_50"].to_dict() if "ma_50" in analysis["moving_averages"] else {},
                "rsi": {"current": analysis.get("current_rsi", 50)},
                "macd": {
                    "macd": analysis["macd"]["macd"].tail(100).to_dict() if "macd" in analysis["macd"] else {},
                    "signal": analysis["macd"]["signal"].tail(100).to_dict() if "signal" in analysis["macd"] else {}
                }
            }
        
        # Add signal history
        performance = fetcher.get_signal_performance(symbol, lookback_days=365)
        result["signal_history"] = performance
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/scan/sector")
def scan_sector(
    sector: str,
    min_confidence: float = 0.6,
    strategy: str = "comprehensive",
    limit: int = 20,
    x_api_key: Optional[str] = Header(None)
):
    """
    Scan all stocks in a specific sector
    
    Args:
        sector: GICS sector name
        min_confidence: Minimum confidence threshold
        strategy: Scanning strategy
        limit: Maximum results to return
        x_api_key: API key for authentication
    """
    verify_api_key(x_api_key)
    check_rate_limit("scan_sector")
    
    try:
        # Validate sector
        sector_enum = None
        for sec in Sector:
            if sec.value == sector:
                sector_enum = sec
                break
        
        if not sector_enum:
            raise HTTPException(status_code=400, detail=f"Invalid sector: {sector}")
        
        # Initialize scanner
        loader = DataLoader()
        scanner = MarketScanner(data_loader=loader)
        
        # Scan sector
        results = scanner.scan_by_sectors(
            sectors=[sector_enum],
            min_confidence=min_confidence,
            strategy=strategy,
            limit_per_sector=limit,
            use_cache=True
        )
        
        # Format response
        opportunities = results.get(sector, [])
        
        return {
            "sector": sector,
            "total_scanned": len(MARKET_SYMBOLS.get(sector_enum, [])),
            "opportunities_found": len(opportunities),
            "min_confidence": min_confidence,
            "opportunities": opportunities[:limit]
        }
        
    except Exception as e:
        logger.error(f"Error scanning sector {sector}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/market/overview")
def market_overview():
    """
    Get market overview with top opportunities across all sectors
    """
    try:
        # Check cache first
        cache_key = _get_dashboard_cache_key(threshold, sectors, asset_types, demo)
        if cache_key in dashboard_cache:
            logger.info(f"Dashboard cache hit for key: {cache_key}")
            cached_result = dashboard_cache[cache_key]
            return templates.TemplateResponse(
                "dashboard.html",
                {
                    "request": request,
                    "opportunities": cached_result["opportunities"],
                    "on_sale": cached_result["on_sale"],
                    "overbought": cached_result["overbought"],
                    "title": "Premium Trading Dashboard",
                    "threshold": threshold,
                    "count": cached_result["count"],
                    "failed_sources": cached_result["failed_sources"],
                    "demo_mode": demo,
                    "asset_type_counts": cached_result["asset_type_counts"],
                },
            )
        
        loader = DataLoader()
        scanner = MarketScanner(data_loader=loader)
        
        # Get top opportunities from each sector
        sector_opportunities = {}
        
        for sector in Sector:
            # Get top 3 from each sector
            symbols = list(MARKET_SYMBOLS[sector])[:10]  # Scan top 10, return top 3
            
            opportunities = scanner.scan_stocks(
                symbols=symbols,
                min_confidence=0.5,
                asset_type=AssetType.STOCK.value
            )
            
            if opportunities:
                sector_opportunities[sector.value] = opportunities[:3]
        
        # Get crypto, forex, commodities highlights
        other_opportunities = {
            "crypto": scanner.scan_stocks(
                symbols=CRYPTO_SYMBOLS[:5],
                min_confidence=0.5,
                asset_type=AssetType.CRYPTO.value
            )[:3],
            "forex": scanner.scan_stocks(
                symbols=FOREX_PAIRS[:5],
                min_confidence=0.5,
                asset_type=AssetType.FOREX.value
            )[:3],
            "commodities": scanner.scan_stocks(
                symbols=COMMODITIES[:5],
                min_confidence=0.5,
                asset_type=AssetType.METAL.value
            )[:3]
        }
        
        return {
            "timestamp": datetime.now().isoformat(),
            "sectors": sector_opportunities,
            "other_assets": other_opportunities,
            "market_summary": {
                "total_opportunities": sum(len(opps) for opps in sector_opportunities.values()) + 
                                       sum(len(opps) for opps in other_opportunities.values()),
                "top_sectors": sorted(
                    [(sector, len(opps)) for sector, opps in sector_opportunities.items() if opps],
                    key=lambda x: x[1],
                    reverse=True
                )[:3]
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating market overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request, threshold: float = 0.2, demo: bool = False, 
             sectors: Optional[str] = None, asset_types: Optional[str] = None):
    """
    Enhanced dashboard with sector filtering and 200+ symbols support.
    
    Args:
        threshold: Minimum confidence threshold (0.0-1.0). Lower values show more signals.
        demo: If True, force sample data for all symbols (bypasses live data fetch).
        sectors: Comma-separated list of sectors to include (e.g., "Information Technology,Health Care")
        asset_types: Comma-separated list of additional asset types (e.g., "crypto,forex,commodities")
    """
    try:
        # Check cache first
        cache_key = _get_dashboard_cache_key(threshold, sectors, asset_types, demo)
        if cache_key in dashboard_cache:
            logger.info(f"Dashboard cache hit for key: {cache_key}")
            cached_result = dashboard_cache[cache_key]
            return templates.TemplateResponse(
                "dashboard.html",
                {
                    "request": request,
                    "opportunities": cached_result["opportunities"],
                    "on_sale": cached_result["on_sale"],
                    "overbought": cached_result["overbought"],
                    "title": "Premium Trading Dashboard",
                    "threshold": threshold,
                    "count": cached_result["count"],
                    "failed_sources": cached_result["failed_sources"],
                    "demo_mode": demo,
                    "asset_type_counts": cached_result["asset_type_counts"],
                },
            )
        
        loader = DataLoader()
        scanner = MarketScanner(data_loader=loader)
        
        # Build symbol list based on filters
        all_symbols = []
        
        # Process sector filters
        if sectors:
            selected_sectors = [s.strip() for s in sectors.split(",")]
            for sector in Sector:
                if sector.value in selected_sectors:
                    all_symbols.extend(MARKET_SYMBOLS[sector])
        else:
            # Default: use a subset of symbols from each sector
            for sector, symbols in MARKET_SYMBOLS.items():
                all_symbols.extend(symbols[:3])  # Top 3 from each sector
        
        # Add additional asset types if selected
        if asset_types:
            selected_types = [t.strip() for t in asset_types.split(",")]
            if "crypto" in selected_types:
                all_symbols.extend(CRYPTO_SYMBOLS[:10])  # Top 10 cryptos
            if "forex" in selected_types:
                all_symbols.extend(FOREX_PAIRS[:10])    # Top 10 forex pairs
            if "commodities" in selected_types:
                all_symbols.extend(COMMODITIES[:8])     # Top 8 commodities
        
        # Ensure threshold is valid (0.0 to 1.0)
        threshold = max(0.0, min(1.0, threshold))
        
        # Track failed data sources
        failed_sources = []
        asset_type_counts = {}
        
        if demo:
            logger.info("Demo mode active: Using sample data for all symbols")
        
        # Group symbols by asset type
        symbols_by_type = {}
        for symbol in all_symbols:
            asset_type = _get_asset_type(symbol)
            if asset_type.value not in symbols_by_type:
                symbols_by_type[asset_type.value] = []
            symbols_by_type[asset_type.value].append(symbol)
        
        # Scan each asset type separately
        all_opps = []
        for asset_type_value, symbols in symbols_by_type.items():
            try:
                if demo:
                    # Demo mode: use scanner's scan_stocks but it will use sample data
                    opps = scanner.scan_stocks(
                        symbols,
                        min_confidence=threshold,
                        asset_type=asset_type_value,
                        period="6mo" if asset_type_value == AssetType.STOCK.value else "3mo"
                    )
                    all_opps.extend(opps)
                    asset_type_counts[asset_type_value] = len(opps)
                    logger.info(f"[DEMO] {asset_type_value}: {len(opps)} opportunities from {len(symbols)} symbols")
                else:
                    # Normal mode: let scanner handle data fetching and fallback to sample data
                    opps = scanner.scan_stocks(
                        symbols,
                        min_confidence=threshold,
                        asset_type=asset_type_value,
                        period="6mo" if asset_type_value == AssetType.STOCK.value else "3mo"
                    )
                    all_opps.extend(opps)
                    asset_type_counts[asset_type_value] = len(opps)
                    logger.info(f"{asset_type_value}: {len(opps)} opportunities from {len(symbols)} symbols")
            except Exception as e:
                logger.error(f"Error scanning {asset_type_value} symbols: {e}")
                failed_sources.append(f"{asset_type_value}_scanner")
        
        # Categorize opportunities
        categorized = _categorize_opportunities(all_opps)
        
        # Store in cache
        dashboard_cache[cache_key] = {
            "opportunities": all_opps,
            "on_sale": categorized["on_sale"],
            "overbought": categorized["overbought"],
            "count": len(all_opps),
            "failed_sources": failed_sources,
            "asset_type_counts": asset_type_counts,
        }
        logger.info(f"Dashboard results cached with key: {cache_key}")
        
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "opportunities": all_opps,
                "on_sale": categorized["on_sale"],
                "overbought": categorized["overbought"],
                "title": "Premium Trading Dashboard",
                "threshold": threshold,
                "count": len(all_opps),
                "failed_sources": failed_sources,
                "demo_mode": demo,
                "asset_type_counts": asset_type_counts,
            },
        )
    except Exception as e:
        logger.error(f"Dashboard error: {e}", exc_info=True)
        # Return error page
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request,
                "opportunities": [],
                "on_sale": [],
                "overbought": [],
                "title": "Premium Trading Dashboard - Error",
                "threshold": threshold,
                "count": 0,
                "failed_sources": [f"Dashboard error: {str(e)}"],
                "demo_mode": False,
                "asset_type_counts": {},
                "error": str(e),
            },
        )



@app.post("/api/watchlist")
def add_to_watchlist(symbol: str = Query(...)):
    """
    Add a symbol to the watchlist
    
    Args:
        symbol: Stock/crypto/forex symbol to add
    """
    try:
        watchlist_file = "data/watchlist.json"
        os.makedirs("data", exist_ok=True)
        
        # Load existing watchlist
        watchlist = []
        if os.path.exists(watchlist_file):
            with open(watchlist_file, "r") as f:
                watchlist = json.load(f)
        
        # Add symbol if not already present
        if symbol.upper() not in [s.upper() for s in watchlist]:
            watchlist.append(symbol.upper())
            with open(watchlist_file, "w") as f:
                json.dump(watchlist, f, indent=2)
            logger.info(f"Added {symbol} to watchlist")
            return {"status": "success", "message": f"{symbol} added to watchlist", "watchlist": watchlist}
        else:
            return {"status": "exists", "message": f"{symbol} already in watchlist", "watchlist": watchlist}
    except Exception as e:
        logger.error(f"Error adding to watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/watchlist")
def get_watchlist():
    """Get the current watchlist"""
    try:
        watchlist_file = "data/watchlist.json"
        watchlist = []
        if os.path.exists(watchlist_file):
            with open(watchlist_file, "r") as f:
                watchlist = json.load(f)
        return {"watchlist": watchlist, "count": len(watchlist)}
    except Exception as e:
        logger.error(f"Error getting watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/watchlist/{symbol}")
def remove_from_watchlist(symbol: str):
    """
    Remove a symbol from the watchlist
    
    Args:
        symbol: Stock/crypto/forex symbol to remove
    """
    try:
        watchlist_file = "data/watchlist.json"
        if not os.path.exists(watchlist_file):
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        # Load existing watchlist
        with open(watchlist_file, "r") as f:
            watchlist = json.load(f)
        
        # Remove symbol (case-insensitive)
        original_count = len(watchlist)
        watchlist = [s for s in watchlist if s.upper() != symbol.upper()]
        
        if len(watchlist) < original_count:
            with open(watchlist_file, "w") as f:
                json.dump(watchlist, f, indent=2)
            logger.info(f"Removed {symbol} from watchlist")
            return {"status": "success", "message": f"{symbol} removed from watchlist", "watchlist": watchlist}
        else:
            raise HTTPException(status_code=404, detail=f"{symbol} not found in watchlist")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing from watchlist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/logs")
async def receive_logs(request: Request):
    """
    Receive and store client-side logs for debugging.
    Logs are stored in logs/modal_debug_YYYY-MM-DD.json
    """
    try:
        body = await request.json()
        logs = body.get("logs", [])
        
        if not logs:
            return JSONResponse({"status": "ok", "message": "No logs to store"})
        
        # Create logs directory if it doesn't exist
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        
        # Use today's date for log file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = logs_dir / f"modal_debug_{today}.json"
        
        # Read existing logs if file exists
        existing_logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            except (json.JSONDecodeError, IOError):
                # If file is corrupted or empty, start fresh
                existing_logs = []
        
        # Append new logs
        existing_logs.extend(logs)
        
        # Write back to file
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, indent=2, ensure_ascii=False)
        
        logger.debug(f"Stored {len(logs)} log entries to {log_file}")
        
        return JSONResponse({
            "status": "ok",
            "message": f"Stored {len(logs)} log entries",
            "log_file": str(log_file)
        })
        
    except Exception as e:
        logger.error(f"Error storing logs: {e}")
        # Don't raise exception - we don't want logging failures to break the app
        return JSONResponse({"status": "error", "message": str(e)})


@app.get("/api/logs/latest")
def get_latest_logs():
    """
    Retrieve the most recent log file for debugging.
    """
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return JSONResponse({"status": "error", "message": "Logs directory does not exist"})
        
        # Find most recent log file
        log_files = sorted(logs_dir.glob("modal_debug_*.json"), reverse=True)
        
        if log_files:
            latest_file = log_files[0]
            with open(latest_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            return JSONResponse({
                "status": "ok",
                "log_file": str(latest_file),
                "entry_count": len(logs),
                "logs": logs[-100:]  # Return last 100 entries
            })
        else:
            return JSONResponse({"status": "ok", "message": "No log files found", "logs": []})
            
    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/report/{symbol}")
def generate_pdf_report(symbol: str, signal_type: Optional[str] = None):
    """
    Generate and download PDF report for a symbol
    
    Args:
        symbol: Stock/crypto/forex symbol
        signal_type: Optional signal type (BUY/SELL/HOLD) to use for analysis
    """
    # #region agent log
    import json
    log_path = "/Users/freedom/QUANTS/.cursor/debug.log"
    try:
        with open(log_path, "a") as f:
            f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "A", "location": "api_service.py:906", "message": "generate_pdf_report_entry", "data": {"symbol": symbol, "signal_type": signal_type}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
    except: pass
    # #endregion agent log
    try:
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "A", "location": "api_service.py:918", "message": "before_import_pdf_generator", "data": {"symbol": symbol}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        from fastapi.responses import FileResponse
        from src.utils.pdf_generator import PDFGenerator
        
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "A", "location": "api_service.py:922", "message": "after_import_pdf_generator", "data": {"symbol": symbol, "import_success": True}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        
        # Initialize components
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "D", "location": "api_service.py:925", "message": "before_initialize_components", "data": {"symbol": symbol}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        loader = DataLoader()
        analyzer = DetailedAnalyzer(loader)
        historical_fetcher = HistoricalFetcher()
        pdf_gen = PDFGenerator()
        
        # Determine asset type
        asset_type = _get_asset_type(symbol)
        
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "E", "location": "api_service.py:933", "message": "before_fetch_historical", "data": {"symbol": symbol, "asset_type": asset_type}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        
        # Fetch historical data
        historical_data = historical_fetcher.fetch_historical_data(
            symbol, asset_type, years=1, use_cache=True
        )
        
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "E", "location": "api_service.py:940", "message": "after_fetch_historical", "data": {"symbol": symbol, "has_data": historical_data is not None, "data_length": len(historical_data) if historical_data is not None else 0}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        
        if historical_data is None or len(historical_data) < 50:
            # #region agent log
            try:
                with open(log_path, "a") as f:
                    f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "E", "location": "api_service.py:943", "message": "insufficient_data_error", "data": {"symbol": symbol, "data_length": len(historical_data) if historical_data is not None else 0}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
            except: pass
            # #endregion agent log
            raise HTTPException(status_code=404, detail=f"Insufficient data for {symbol}")
        
        # Get current price
        current_price = float(historical_data["close"].iloc[-1])
        
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "D", "location": "api_service.py:950", "message": "before_generate_analysis", "data": {"symbol": symbol, "current_price": current_price}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        
        # Generate comprehensive analysis
        analysis = analyzer.generate_comprehensive_analysis(
            symbol=symbol,
            current_price=current_price,
            historical_data=historical_data,
            signal_type=signal_type
        )
        
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "D", "location": "api_service.py:960", "message": "after_generate_analysis", "data": {"symbol": symbol, "has_analysis": analysis is not None}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "A", "location": "api_service.py:963", "message": "before_generate_pdf", "data": {"symbol": symbol}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        
        # Generate PDF
        pdf_path = pdf_gen.generate_report(symbol, analysis)
        
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "A", "location": "api_service.py:968", "message": "after_generate_pdf", "data": {"symbol": symbol, "pdf_path": pdf_path}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        
        # Return file for download
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{symbol}_analysis_report.pdf"
        )
        
    except ImportError as e:
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "A", "location": "api_service.py:980", "message": "import_error_caught", "data": {"symbol": symbol, "error_message": str(e), "error_type": type(e).__name__}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        logger.error(f"PDF generation not available: {e}")
        raise HTTPException(
            status_code=503,
            detail="PDF generation requires reportlab. Install with: pip install reportlab"
        )
    except Exception as e:
        # #region agent log
        try:
            with open(log_path, "a") as f:
                f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "B", "location": "api_service.py:987", "message": "general_exception_caught", "data": {"symbol": symbol, "error_message": str(e), "error_type": type(e).__name__}, "timestamp": int(datetime.now().timestamp() * 1000)}) + "\n")
        except: pass
        # #endregion agent log
        logger.error(f"Error generating PDF report for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/gallery", response_class=HTMLResponse)
def gallery(request: Request):
    """
    Image gallery for generated charts (served from output/).
    """
    output_dir = "output"
    files = []
    if os.path.isdir(output_dir):
        files = sorted(
            [f for f in os.listdir(output_dir) if f.lower().endswith(".png")]
        )
    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "files": files,
            "title": "Chart Gallery",
        },
    )
