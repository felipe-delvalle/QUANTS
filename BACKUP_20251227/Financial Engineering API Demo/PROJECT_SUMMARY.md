# 📊 Financial Engineering API Demo – Comprehensive Summary

End-to-end demo of multi-API market data, portfolio/risk analytics, scanning, and a FastAPI dashboard with caching and lightweight vs. full analysis paths.

## Architecture & Entrypoints
- `api_service.py`: FastAPI app, dashboard/analysis endpoints, shared singleton-style `HistoricalFetcher` and `MarketScanner`, dashboard caching, NaN-safe JSON responses.
- `main.py`: demo runner; `cli.py`: command-line interface; `build.sh` / `restart_server.sh`: packaging/runtime helpers.
- Config: `src/config/` holds enums (`AssetType`), retry/backoff defaults, and settings loader.

## Project Structure (High Level)
- `src/api_clients/` (Alpha Vantage, Yahoo, GitHub + base client).
- `src/analysis/` (portfolio, risk, optimization, advanced indicators).
- `src/trading/` (scanner, signals, technical indicators).
- `src/backtesting/` (engine + config), `src/orchestrator/` (workflow).
- `templates/` and `static/js/` (dashboard, modal, logging), `output/` (reports).
- Root helpers: `build.sh`, `requirements.txt`, `.env.example`, `README.md`, `QUICK_START.md`.

## Data & Fetching
- `src/data/data_loader.py`: resilient DataLoader with retries/backoff, Yahoo Finance default; optional crypto/forex/metals clients guarded by try/except to avoid crashes; routes by asset type.
- `src/data/historical_fetcher.py`: OHLCV fetcher using bounded `TTLCache(maxsize=100, ttl=300)` plus `clear()`; prevents unbounded memory.
- `src/data/__init__.py`: exports DataLoader from `data_loader.py` to keep imports aligned.

## API Clients
- `src/api_clients/`: Yahoo, Alpha Vantage, GitHub; base client for shared logic. Optional clients are conditionally used.
- Coverage: Yahoo (market data, company info, financials, history), Alpha Vantage (quotes, history, indicators, symbol search), GitHub (repo ops, issues, commits, releases); base client handles rate limiting/caching/error handling.

## Trading & Scanning
- `src/trading/market_scanner.py`: scanning engine; supports `full_analysis` (heavy) vs lightweight scans; shorter lookbacks for dashboard/overview; uses shared fetcher cache; caps symbol counts and trims sector/asset lists.
- `signal_generator.py`, `technical_indicators.py`: signal and indicator calculations supporting scans.

## Analysis Engine
- `src/analysis/detailed_analyzer.py`: full per-symbol deep dive for modal requests.
- `portfolio.py`, `risk_metrics.py`, `optimization.py`, `advanced_indicators.py`: portfolio analytics, risk metrics, optimization, and advanced factors.

## Backtesting & Orchestration
- `src/backtesting/backtest_engine.py` (+ config): historical strategy evaluation.
- `src/orchestrator/workflow.py`: coordinates multi-step workflows across fetch → analysis → report.

## Utilities & Support
- `src/utils/`: `cache_manager.py` (TTL/LRU helpers), `pdf_generator.py`, misc helpers.
- Scripts: `stop_server.sh`, `restart_server.sh`, server command references in `SERVER_COMMANDS.md`.
- Output/docs: generated reports in `output/`; guides (`QUICK_START.md`, `CODE_REVIEW.md`, `PROJECT_SUMMARY.md` updated here).

## Frontend (Dashboard & Modal)
- Templates: `templates/dashboard.html` (sections “📈 On Sale / Buy Opportunity” and “📉 Overbought / Sell Oportunities”), `templates/components/analysis_modal.html`, `home.html`.
- Static JS: `static/js/analysis_modal.js` for modal logic and indicator rendering; `static/js/logger.js` gated logger (disabled unless explicitly enabled via `localStorage.enableClientLogger=true` or `window.ENABLE_CLIENT_LOGGER=true`).

## Runtime Behavior & Optimizations (Recent)
- Shared, long-lived `HistoricalFetcher` and `MarketScanner` to reuse cached history/quotes across requests.
- Bounded caches: `HistoricalFetcher` TTL cache; `dashboard_cache` size reduced (64) to cut memory pressure.
- Lightweight vs full analysis: dashboard/overview use quick scans with shorter lookbacks and fewer symbols; full analysis deferred to `/api/analysis/{symbol}`.
- JSON safety: pandas Series converted to dict with NaN→None before responses to avoid serialization errors.
- Optional clients: guarded imports/use to prevent `ModuleNotFoundError` when optional deps are absent.

## API Surface (High Level)
- `/dashboard`, `/overview`: render cached opportunities via lightweight scans.
- `/api/historical/{symbol}`: historical data + indicators (SMA, MACD, RSI) NaN-safe.
- `/api/analysis/{symbol}`: full detailed analysis on demand.
- `/scan`: scanning endpoint; toggles `full_analysis` and lookback; uses shared scanner/fetcher.
- Logging endpoint available but frontend logger is gated off by default.

## Usage Examples
- Quick start: `./build.sh`, configure `.env`, `python main.py` (or `./restart_server.sh`), optional venv activation.
- CLI: `python cli.py quote AAPL --source yahoo` (or `--source alpha`).
- Programmatic: instantiate `YahooFinanceClient` or `PortfolioAnalyzer`, fetch a quote, then analyze a portfolio.

## API Keys
- Alpha Vantage key required (free tier 5 req/min).
- GitHub PAT for repo/issue/commit/release operations.
- Yahoo Finance: no key required.

## Setup, Run, Test
- Requirements: `python >= 3.9`, `pip install -r requirements.txt`.
- Env: copy `.env.example` → `.env` (Alpha Vantage key, optional API keys).
- Run server: `python api_service.py` or `./restart_server.sh`; CLI: `python cli.py --help`.
- Tests: `pytest` (coverage optional).
- Docker: optional build/run (see README if Dockerfile present).

## Features Demonstrated
- Multi-API integration with unified interfaces and rate limiting.
- Financial engineering: portfolio analysis, optimization, risk metrics (VaR, CVaR, Sharpe).
- Workflow automation/orchestration and build automation.
- Clean architecture, caching, and environment-driven configuration.

## Status
- Project is demo-ready/complete; extend with additional APIs or analysis modules as needed.

## Operational Notes
- Memory: bounded caches plus symbol caps mitigate growth; `HistoricalFetcher.clear()` available if needed.
- UI labels updated; client logger off by default to reduce noise.
- Commit reminders: use `./.scripts/auto_commit.sh` or `gac "msg"` after changes.
