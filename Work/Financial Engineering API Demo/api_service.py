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
from typing import List, Optional, Dict, Any
import os
from datetime import datetime
from fastapi import FastAPI, HTTPException, Header, Request, Query
from pydantic import BaseModel
from cachetools import TTLCache
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from src.config import get_settings, configure_logging, AssetType
from src.data import DataLoader
from src.trading.market_scanner import MarketScanner
from src.data.market_symbols import Sector, MARKET_SYMBOLS, CRYPTO_SYMBOLS, FOREX_PAIRS, COMMODITIES
from src.data.historical_fetcher import HistoricalFetcher
from src.analysis import DetailedAnalyzer, ReportGenerator
from src.analysis.yield_curve import YieldCurve, CurveFactory, IndexCurveFactory, IndexRegistry
from src.api_clients.fred_api import FREDClient
from src.analysis.advanced_indicators import AdvancedIndicators
from src.backtesting import BacktestEngine
from src.api_clients.yahoo_finance import YahooFinanceClient
import pandas as pd

try:
    import psutil  # Optional; used for monitoring
except ImportError:  # pragma: no cover
    psutil = None

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

# Cache settings for shared loaders
PRELOAD_RETENTION_SECONDS = 720  # cache TTL for shared loader/fetcher

# Shared data loader and scanners to reuse caches across requests
shared_loader = DataLoader(cache_ttl_seconds=PRELOAD_RETENTION_SECONDS)
shared_historical_fetcher = HistoricalFetcher()
shared_historical_fetcher.cache = TTLCache(maxsize=1000, ttl=720)
shared_scanner = MarketScanner(data_loader=shared_loader, historical_fetcher=shared_historical_fetcher)




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


class BondPriceRequest(BaseModel):
    face_value: float = 1000.0
    coupon_rate_pct: float
    years_to_maturity: float
    frequency: int = 2
    market_rate_pct: Optional[float] = None
    price: Optional[float] = None
    market: Optional[str] = "US Treasuries"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/monitor")
def monitor():
    """Lightweight monitoring: cache sizes and process memory."""
    process_mem_mb = None
    if psutil:
        try:
            process = psutil.Process(os.getpid())
            process_mem_mb = round(process.memory_info().rss / (1024 * 1024), 2)
        except Exception:
            process_mem_mb = None
    return {
        "caches": {
            "historical_fetcher": {"size": len(shared_historical_fetcher.cache), "ttl": shared_historical_fetcher.cache.ttl},
            "data_loader": {"size": len(shared_loader.cache), "ttl": shared_loader.cache.ttl},
        },
        "resources": {"process_mem_mb": process_mem_mb},
    }


@app.post("/scan")
def scan(req: ScanRequest, x_api_key: Optional[str] = Header(None)):
    verify_api_key(x_api_key)
    check_rate_limit("scan")

    opps = shared_scanner.scan_stocks(
        req.symbols,
        min_confidence=req.min_confidence,
        strategy=req.strategy,
        asset_type=req.asset_type.value,
        period=req.period,
        full_analysis=True,
        historical_years=1.0
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
                {"method": "GET", "path": "/bond-pricer", "desc": "Bond pricer for US/EU"},
                {"method": "GET", "path": "/yield-curve", "desc": "Interest rate curve calculator"},
                {"method": "GET", "path": "/gallery", "desc": "PDF reports gallery"},
                {"method": "GET", "path": "/health", "desc": "Health check"},
                {"method": "GET", "path": "/", "desc": "API root"},
                {"method": "POST", "path": "/scan", "desc": "Scan for trading opportunities (requires API key)"},
                {"method": "POST", "path": "/backtest", "desc": "Backtest strategies (requires API key)"},
            ],
        },
    )


def _build_bond_cashflows(face_value: float, coupon_rate_pct: float, years_to_maturity: float, frequency: int) -> List[Dict[str, float]]:
    periods = max(int(round(years_to_maturity * frequency)), 1)
    coupon_payment = face_value * (coupon_rate_pct / 100.0) / frequency
    cashflows = []
    for n in range(1, periods + 1):
        cashflow = coupon_payment
        if n == periods:
            cashflow += face_value
        cashflows.append({
            "period": n,
            "cashflow": cashflow,
            "time_years": n / frequency
        })
    return cashflows


def _price_from_rate(cashflows: List[Dict[str, float]], rate_pct: float, frequency: int) -> Optional[float]:
    if rate_pct is None:
        return None
    rate_decimal = rate_pct / 100.0
    total = 0.0
    for item in cashflows:
        discount = (1 + rate_decimal / frequency) ** item["period"]
        total += item["cashflow"] / discount
    return total


def _ytm_from_price(cashflows: List[Dict[str, float]], target_price: float, frequency: int, max_rate: float = 0.3) -> Optional[float]:
    """
    Solve for yield to maturity (annualized, percent) via binary search.
    """
    if target_price is None or target_price <= 0 or not cashflows:
        return None
    
    low = 0.0
    high = max_rate
    mid = 0.0
    for _ in range(80):
        mid = (low + high) / 2
        price_estimate = _price_from_rate(cashflows, mid * 100, frequency)
        if price_estimate is None:
            return None
        if abs(price_estimate - target_price) < 1e-4:
            break
        if price_estimate > target_price:
            low = mid
        else:
            high = mid
    return mid * 100


def _macaulay_duration(cashflows: List[Dict[str, float]], rate_pct: Optional[float], frequency: int, price: Optional[float]) -> Optional[float]:
    if rate_pct is None or price is None or price <= 0:
        return None
    rate_decimal = rate_pct / 100.0
    numerator = 0.0
    for item in cashflows:
        discount = (1 + rate_decimal / frequency) ** item["period"]
        pv = item["cashflow"] / discount
        numerator += item["time_years"] * pv
    return numerator / price


BOND_MARKETS = ["US Treasuries", "EU Gov"]

BOND_PRESETS = {
    "US Treasuries": [
        {"id": "ust-2y", "name": "US Treasury 2Y", "face_value": 1000, "coupon_rate_pct": 4.2, "years_to_maturity": 2.0, "frequency": 2, "market_rate_pct": 4.1, "price": None},
        {"id": "ust-5y", "name": "US Treasury 5Y", "face_value": 1000, "coupon_rate_pct": 3.8, "years_to_maturity": 5.0, "frequency": 2, "market_rate_pct": 3.9, "price": None},
        {"id": "ust-10y", "name": "US Treasury 10Y", "face_value": 1000, "coupon_rate_pct": 4.0, "years_to_maturity": 10.0, "frequency": 2, "market_rate_pct": 4.2, "price": None},
    ],
    "EU Gov": [
        {"id": "bund-5y", "name": "Bund 5Y", "face_value": 1000, "coupon_rate_pct": 2.5, "years_to_maturity": 5.0, "frequency": 1, "market_rate_pct": 2.4, "price": None},
        {"id": "bund-10y", "name": "Bund 10Y", "face_value": 1000, "coupon_rate_pct": 2.8, "years_to_maturity": 10.0, "frequency": 1, "market_rate_pct": 2.6, "price": None},
        {"id": "oat-7y", "name": "France OAT 7Y", "face_value": 1000, "coupon_rate_pct": 2.9, "years_to_maturity": 7.0, "frequency": 1, "market_rate_pct": 2.7, "price": None},
    ],
}


@app.get("/bond-pricer", response_class=HTMLResponse)
def bond_pricer_page(request: Request):
    return templates.TemplateResponse(
        "bond_pricer.html",
        {
            "request": request,
            "title": "Bond Pricer (US & EU)",
            "markets": BOND_MARKETS,
            "presets": BOND_PRESETS,
            "presets_json": json.dumps(BOND_PRESETS),
        },
    )


@app.get("/yield-curve", response_class=HTMLResponse)
def yield_curve_page(request: Request):
    """Yield curve calculator page"""
    return templates.TemplateResponse(
        "yield_curve.html",
        {
            "request": request,
            "title": "Interest Rate Curve Calculator",
        },
    )


class YieldCurveRequest(BaseModel):
    tenors: Optional[List[float]] = None
    rates: Optional[List[float]] = None
    bonds: Optional[List[Dict[str, Any]]] = None
    interpolation: str = "cubic_spline"
    compounding: str = "simple"


class IndexCurveRequest(BaseModel):
    """Request for index-based curve construction (Murex-style)"""
    index_code: Optional[str] = None  # Single index (e.g., "SOFR")
    index_rates: Optional[Dict[str, List[Dict[str, Any]]]] = None  # Multiple indexes
    primary_index: Optional[str] = None  # Primary index for multi-index curves
    interpolation: str = "cubic_spline"
    day_count: Optional[str] = None
    compounding: Optional[str] = None


@app.get("/api/yield-curve/fetch-real")
def fetch_real_treasury_yields():
    """
    Fetch real US Treasury yields from FRED API.
    Fast implementation with caching and parallel requests.
    """
    try:
        if not settings.fred_api_key:
            raise HTTPException(
                status_code=400,
                detail="FRED API key not configured. Add FRED_API_KEY to your .env file. Get a free key at https://fred.stlouisfed.org/docs/api/api_key.html"
            )

        fred_client = FREDClient(api_key=settings.fred_api_key)
        data = fred_client.get_yield_curve_data()
        
        return {
            "success": True,
            "data": data,
            "message": "Real market data fetched successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching FRED data: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch Treasury yields: {str(e)}")


@app.get("/api/yield-curve/presets")
def get_yield_curve_presets():
    """
    Get available yield curve presets with real market data where available.
    Returns example curves for demonstration purposes.
    """
    try:
        # Try to fetch real US Treasury data using yfinance
        real_ust_data = None
        try:
            import yfinance as yf
            # US Treasury symbols: ^IRX (3mo), ^FVX (5Y), ^TNX (10Y), ^TYX (30Y)
            # Note: yfinance has limited Treasury data, so we'll use example data
            # In production, you'd use a Treasury API like FRED or TreasuryDirect
            pass
        except:
            pass
        
        # Return presets using official Treasury terminology
        # Official names per U.S. Treasury: "Market Yield on U.S. Treasury Securities at X-Year Constant Maturity"
        # Standard yield curve shapes: Normal, Inverted, Steep, Flat, Humped
        return {
            "presets": {
                "ust_par_yield_curve": {
                    "name": "Treasury Par Yield Curve",
                    "description": "U.S. Treasury Par Yield Curve (Constant Maturity Rates)",
                    "source": "U.S. Department of the Treasury methodology",
                    "tenors": [0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30],
                    "rates": [5.25, 5.30, 5.35, 5.20, 5.10, 4.95, 4.85, 4.75, 4.90, 4.95],
                },
                "ust_normal_yield_curve": {
                    "name": "Normal Yield Curve",
                    "description": "Upward-sloping yield curve (normal market conditions)",
                    "source": "Standard yield curve shape",
                    "tenors": [0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30],
                    "rates": [2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.4, 3.5],
                },
                "ust_inverted_yield_curve": {
                    "name": "Inverted Yield Curve",
                    "description": "Downward-sloping yield curve (recession indicator)",
                    "source": "Standard yield curve shape",
                    "tenors": [0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30],
                    "rates": [5.5, 5.4, 5.3, 5.2, 5.1, 5.0, 4.9, 4.8, 4.7, 4.6],
                },
                "euro_area_government_bonds": {
                    "name": "Euro Area Government Bond Yields",
                    "description": "Eurozone sovereign bond yield curve",
                    "source": "ECB methodology",
                    "tenors": [0.25, 0.5, 1, 2, 3, 5, 7, 10, 15, 20],
                    "rates": [3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0, 4.1],
                }
            },
            "note": "Reference yield curves for analysis. For live market data, use the 'Fetch Real Treasury Yields (FRED)' button."
        }
    except Exception as e:
        logger.error(f"Error getting presets: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get presets: {str(e)}")


@app.post("/api/yield-curve/calculate")
def calculate_yield_curve(req: YieldCurveRequest):
    """
    Calculate yield curve metrics from tenors/rates or bootstrap from bonds.
    """
    try:
        if req.bonds is not None:
            # Bootstrap from bonds
            curve = CurveFactory.create_from_bonds(
                bonds=req.bonds,
                bootstrapper_type="bond",
                interpolation=req.interpolation,
                compounding=req.compounding,
            )
        elif req.tenors is not None and req.rates is not None:
            # Create from manual input
            curve = CurveFactory.create_spot_curve(
                tenors=req.tenors,
                rates=req.rates,
                interpolation=req.interpolation,
                compounding=req.compounding,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Provide either (tenors, rates) or bonds",
            )

        # Calculate metrics - use interpolation/extrapolation to get values
        max_tenor = float(curve.tenors.max())
        min_tenor = float(curve.tenors.min())
        
        # Calculate 3-year metrics (will interpolate/extrapolate if needed)
        spot_3y = None
        df_3y = None
        zc_price_3y = None
        try:
            spot_3y = curve.spot_rate(3.0)
            df_3y = curve.discount_factor(3.0)
            zc_price_3y = curve.zero_coupon_price(3.0, 100.0)
        except Exception as e:
            logger.warning(f"Could not calculate 3-year metrics: {e}")
        
        # Calculate forward rate (2Y to 5Y) - will extrapolate if needed
        forward_2y_5y = None
        try:
            if max_tenor >= 2.0:
                # Try to get forward rate, extrapolating if needed
                forward_2y_5y = curve.forward_rate(2.0, 5.0)
        except Exception as e:
            logger.warning(f"Could not calculate forward rate 2Y->5Y: {e}")
            # Try a shorter forward rate if 5Y is too far
            if max_tenor >= 2.0:
                try:
                    # Use max_tenor if it's between 2 and 5, or use 2.5 if max is less
                    end_tenor = min(5.0, max(2.5, max_tenor))
                    if end_tenor > 2.0:
                        forward_2y_5y = curve.forward_rate(2.0, end_tenor)
                except:
                    pass

        # Build curve data table with all points
        curve_data = []
        for i, (tenor, rate) in enumerate(zip(curve.tenors, curve.rates)):
            try:
                df = curve.discount_factor(tenor)
                curve_data.append({
                    "tenor": float(tenor),
                    "rate": float(rate),
                    "discount_factor": float(df),
                })
            except Exception as e:
                logger.warning(f"Error calculating discount factor for tenor {tenor}: {e}")

        # Add some interpolated points for better visualization
        if len(curve_data) > 0:
            # Add midpoint if there's a gap
            if max_tenor > min_tenor:
                mid_tenor = (min_tenor + max_tenor) / 2
                if mid_tenor not in [p["tenor"] for p in curve_data]:
                    try:
                        mid_rate = curve.spot_rate(mid_tenor)
                        mid_df = curve.discount_factor(mid_tenor)
                        curve_data.append({
                            "tenor": float(mid_tenor),
                            "rate": float(mid_rate),
                            "discount_factor": float(mid_df),
                        })
                        # Sort by tenor
                        curve_data.sort(key=lambda x: x["tenor"])
                    except:
                        pass

        return {
            "spot_3y": spot_3y,
            "df_3y": df_3y,
            "forward_2y_5y": forward_2y_5y,
            "zc_price_3y": zc_price_3y,
            "curve_data": curve_data,
            "max_tenor": max_tenor,
            "min_tenor": min_tenor,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating yield curve: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to calculate yield curve: {str(e)}")


@app.get("/api/yield-curve/indexes")
def list_available_indexes(currency: Optional[str] = None):
    """
    List available interest rate indexes (similar to Murex index definitions).
    
    Args:
        currency: Optional currency filter (USD, EUR, GBP, etc.)
        
    Returns:
        Dict of available indexes with their properties
    """
    try:
        indexes = IndexCurveFactory.list_available_indexes(currency=currency)
        all_indexes = IndexRegistry.list_all()
        
        result = {}
        for code, name in indexes.items():
            index_def = all_indexes[code]
            result[code] = {
                "code": index_def.code,
                "name": index_def.name,
                "currency": index_def.currency,
                "index_type": index_def.index_type.value,
                "day_count": index_def.day_count,
                "compounding": index_def.compounding,
                "fixing_frequency": index_def.fixing_frequency,
                "description": index_def.description,
            }
        
        return {
            "indexes": result,
            "count": len(result),
            "currency_filter": currency,
        }
    except Exception as e:
        logger.error(f"Error listing indexes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list indexes: {str(e)}")


@app.post("/api/yield-curve/from-index")
def calculate_yield_curve_from_index(req: IndexCurveRequest):
    """
    Calculate yield curve from interest rate indexes (Murex-style).
    
    Supports:
    - Single index curve (e.g., SOFR curve)
    - Multi-index curve (combining SOFR, LIBOR, swaps, etc.)
    
    Example single index:
    {
        "index_code": "SOFR",
        "index_rates": {
            "SOFR": [
                {"tenor": 0.25, "rate": 0.05},
                {"tenor": 0.5, "rate": 0.051},
                {"tenor": 1.0, "rate": 0.052}
            ]
        }
    }
    
    Example multi-index:
    {
        "index_rates": {
            "SOFR": [{"tenor": 0.25, "rate": 0.05}],
            "USD-LIBOR-3M": [{"tenor": 0.5, "rate": 0.052}]
        },
        "primary_index": "SOFR"
    }
    """
    try:
        if req.index_code and req.index_rates:
            # Single index specified
            if req.index_code not in req.index_rates:
                raise HTTPException(
                    status_code=400,
                    detail=f"index_code '{req.index_code}' not found in index_rates"
                )
            curve = IndexCurveFactory.create_from_index(
                index_code=req.index_code,
                index_rates=req.index_rates[req.index_code],
                interpolation=req.interpolation,
                day_count=req.day_count,
                compounding=req.compounding,
            )
        elif req.index_rates:
            # Multi-index curve
            curve = IndexCurveFactory.create_from_multiple_indexes(
                index_rates=req.index_rates,
                primary_index=req.primary_index,
                interpolation=req.interpolation,
                day_count=req.day_count or "ACT/360",
                compounding=req.compounding or "simple",
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Provide either index_code with index_rates, or index_rates dict"
            )
        
        # Calculate metrics (same as regular curve)
        max_tenor = float(curve.tenors.max())
        min_tenor = float(curve.tenors.min())
        
        spot_3y = None
        df_3y = None
        zc_price_3y = None
        try:
            spot_3y = curve.spot_rate(3.0)
            df_3y = curve.discount_factor(3.0)
            zc_price_3y = curve.zero_coupon_price(3.0, 100.0)
        except Exception as e:
            logger.warning(f"Could not calculate 3-year metrics: {e}")
        
        forward_2y_5y = None
        try:
            if max_tenor >= 2.0:
                forward_2y_5y = curve.forward_rate(2.0, 5.0)
        except Exception as e:
            logger.warning(f"Could not calculate forward rate 2Y->5Y: {e}")
        
        # Build curve data
        curve_data = []
        for tenor, rate in zip(curve.tenors, curve.rates):
            try:
                df = curve.discount_factor(tenor)
                curve_data.append({
                    "tenor": float(tenor),
                    "rate": float(rate),
                    "discount_factor": float(df),
                })
            except Exception as e:
                logger.warning(f"Error calculating discount factor for tenor {tenor}: {e}")
        
        # Add interpolated points for visualization
        if len(curve_data) > 0 and max_tenor > min_tenor:
            import numpy as np
            interpolated_tenors = np.linspace(min_tenor, max_tenor, 100)
            for t in interpolated_tenors:
                if not any(abs(p["tenor"] - t) < 0.01 for p in curve_data):
                    try:
                        interpolated_rate = curve.spot_rate(t)
                        interpolated_df = curve.discount_factor(t)
                        curve_data.append({
                            "tenor": float(t),
                            "rate": float(interpolated_rate),
                            "discount_factor": float(interpolated_df),
                            "interpolated": True
                        })
                    except Exception:
                        pass
            curve_data.sort(key=lambda x: x["tenor"])
        
        return {
            "spot_3y": spot_3y,
            "df_3y": df_3y,
            "forward_2y_5y": forward_2y_5y,
            "zc_price_3y": zc_price_3y,
            "curve_data": curve_data,
            "min_tenor": min_tenor,
            "max_tenor": max_tenor,
            "curve_type": "index_based",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating index-based yield curve: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to calculate index-based curve: {str(e)}")


@app.post("/api/bond/price")
def price_bond(req: BondPriceRequest):
    """
    Price a plain-vanilla bond and solve YTM if price is provided.
    """
    try:
        cashflows = _build_bond_cashflows(
            face_value=req.face_value,
            coupon_rate_pct=req.coupon_rate_pct,
            years_to_maturity=req.years_to_maturity,
            frequency=req.frequency,
        )
        
        price_from_market = _price_from_rate(cashflows, req.market_rate_pct, req.frequency) if req.market_rate_pct is not None else None
        target_price = req.price if req.price is not None else price_from_market
        
        if target_price is None:
            raise HTTPException(status_code=400, detail="Provide either market_rate_pct (to compute price) or price (to solve YTM).")
        
        ytm_pct = _ytm_from_price(cashflows, target_price, req.frequency)
        if ytm_pct is None and req.market_rate_pct is not None:
            ytm_pct = req.market_rate_pct
        
        current_yield_pct = None
        if target_price > 0:
            annual_coupon = req.face_value * (req.coupon_rate_pct / 100.0)
            current_yield_pct = (annual_coupon / target_price) * 100.0
        
        used_rate = ytm_pct if ytm_pct is not None else req.market_rate_pct
        duration_years = _macaulay_duration(cashflows, used_rate, req.frequency, target_price)
        modified_duration_years = None
        if duration_years is not None and used_rate is not None:
            modified_duration_years = duration_years / (1 + (used_rate / 100.0) / req.frequency)
        
        annotated_cashflows = []
        if used_rate is not None:
            rate_decimal = used_rate / 100.0
            for item in cashflows:
                discount = (1 + rate_decimal / req.frequency) ** item["period"]
                pv = item["cashflow"] / discount
                annotated_cashflows.append({**item, "pv": pv})
        else:
            annotated_cashflows = cashflows
        
        return {
            "inputs": req.dict(),
            "price": target_price,
            "price_from_market": price_from_market,
            "ytm_pct": ytm_pct,
            "current_yield_pct": current_yield_pct,
            "duration_years": duration_years,
            "modified_duration_years": modified_duration_years,
            "cashflows": annotated_cashflows,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pricing bond: {e}")
        raise HTTPException(status_code=500, detail="Failed to price bond")


def _get_asset_type(symbol: str) -> AssetType:
    """Map symbol to its asset type."""
    symbol_upper = symbol.upper()
    
    # Crypto tickers typically use -USD suffix
    if symbol_upper.endswith("-USD"):
        return AssetType.CRYPTO
    
    # Forex pairs use =X suffix
    if symbol_upper.endswith("=X"):
        return AssetType.FOREX
    
    # Commodities futures prefixes
    commodity_prefixes = ("GC=", "SI=", "PL=", "PA=", "CL=", "NG=", "HG=", "ZC=", "ZW=", "ZS=", "SB=", "KC=")
    if symbol_upper.startswith(commodity_prefixes):
        return AssetType.METAL
    
    # Default to stock
    return AssetType.STOCK


def series_to_dict(series: pd.Series) -> dict:
    """Convert pandas Series to a JSON-safe dict, replacing NaN with None."""
    if series is None or len(series) == 0:
        return {}
    return {str(k): (None if pd.isna(v) else float(v)) for k, v in series.items()}



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
        
        # Get current price - use real-time quote instead of stale historical data
        try:
            yahoo_client = YahooFinanceClient()
            quote = yahoo_client.get_quote(symbol)
            current_price = float(quote["price"])
            logger.info(f"Fetched real-time price for {symbol}: ${current_price:.2f}")
        except Exception as e:
            logger.warning(f"Failed to fetch real-time price for {symbol}, using historical close: {e}")
            # Fallback to historical data if quote fetch fails
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
            try:
                from src.trading.technical_indicators import TechnicalAnalyzer
                
                analyzer = TechnicalAnalyzer(data["close"])
                analyzer.set_ohlcv(high=data["high"], low=data["low"], volume=data.get("volume"))
                
                analysis = analyzer.comprehensive_analysis()
                
                moving_averages = analysis.get("moving_averages", {}) if isinstance(analysis, dict) else {}
                ma_20 = moving_averages.get("ma_20")
                ma_50 = moving_averages.get("ma_50")
                macd_data = analysis.get("macd", {}) if isinstance(analysis, dict) else {}
                macd_series = macd_data.get("macd")
                signal_series = macd_data.get("signal")
                current_rsi = analysis.get("current_rsi", 50) if isinstance(analysis, dict) else 50
                rsi_value = 50.0 if pd.isna(current_rsi) else float(current_rsi)

                # Convert series to dict for JSON serialization (NaN -> None)
                result["indicators"] = {
                    "sma_20": series_to_dict(ma_20) if ma_20 is not None else {},
                    "sma_50": series_to_dict(ma_50) if ma_50 is not None else {},
                    "rsi": {"current": rsi_value},
                    "macd": {
                        "macd": series_to_dict(macd_series.tail(100)) if macd_series is not None else {},
                        "signal": series_to_dict(signal_series.tail(100)) if signal_series is not None else {}
                    }
                }
            except Exception as indicator_error:
                logger.error(f"Error calculating indicators for {symbol}: {indicator_error}", exc_info=True)
                # Return basic structure without indicators rather than failing completely
                result["indicators"] = {
                    "sma_20": {},
                    "sma_50": {},
                    "rsi": {"current": 50},
                    "macd": {"macd": {}, "signal": {}}
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
        
        # Scan sector
        results = shared_scanner.scan_by_sectors(
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
        
        # Get current price - use real-time quote instead of stale historical data
        try:
            yahoo_client = YahooFinanceClient()
            quote = yahoo_client.get_quote(symbol)
            current_price = float(quote["price"])
            logger.info(f"Fetched real-time price for {symbol}: ${current_price:.2f}")
        except Exception as e:
            logger.warning(f"Failed to fetch real-time price for {symbol}, using historical close: {e}")
            # Fallback to historical data if quote fetch fails
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
    Gallery of generated PDF reports (served from output/).
    """
    output_dir = "output"
    files = []
    if os.path.isdir(output_dir):
        files = sorted(
            [f for f in os.listdir(output_dir) if f.lower().endswith(".pdf")],
            reverse=True  # Most recent first
        )
    return templates.TemplateResponse(
        "gallery.html",
        {
            "request": request,
            "files": files,
            "title": "PDF Reports Gallery",
        },
    )
