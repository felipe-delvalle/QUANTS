# Financial Engineering API Demo Project

A comprehensive financial engineering project demonstrating multi-API integration, portfolio analysis, and risk management.

## 🎯 Project Overview

This project demonstrates:
- **Multi-API Integration**: Financial data, GitHub, and external services
- **Portfolio Analysis**: Risk metrics, performance analysis, optimization
- **Real-time Data**: Live market data fetching and processing
- **Automated Workflows**: API orchestration and task automation

## 🏗️ Architecture

```
┌─────────────────┐
│  API Clients    │ → Alpha Vantage, Yahoo Finance, GitHub
├─────────────────┤
│  Data Layer     │ → Data fetching, caching, transformation
├─────────────────┤
│  Analysis Engine│ → Portfolio analysis, risk metrics, optimization
├─────────────────┤
│  Orchestrator   │ → Workflow management, API coordination
└─────────────────┘
```

## 📋 Features

- ✅ Multi-source financial data aggregation
- ✅ Portfolio risk analysis (VaR, CVaR, Sharpe Ratio)
- ✅ Real-time market data fetching
- ✅ GitHub API integration for project management
- ✅ Automated report generation
- ✅ RESTful API server
- ✅ CLI interface

## 🚀 Quick Start

### Prerequisites

```bash
python >= 3.9
pip install -r requirements.txt
```

### Installation

```bash
# Clone or navigate to project
cd "Financial Engineering API Demo"

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Configuration

Create `.env` file:

```env
# Financial Data APIs
ALPHA_VANTAGE_API_KEY=your_key_here
YAHOO_FINANCE_ENABLED=true

# GitHub API
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your_username/your_repo

# Optional APIs
FRED_API_KEY=your_fred_key
POLYGON_API_KEY=your_polygon_key
```

### Run

```bash
# Run the demo
python main.py

# Or use the CLI
python cli.py --help

# Start API server
python api_server.py
```

## 📁 Project Structure

```
Financial Engineering API Demo/
├── src/
│   ├── api_clients/
│   │   ├── __init__.py
│   │   ├── alpha_vantage.py      # Alpha Vantage API client
│   │   ├── yahoo_finance.py      # Yahoo Finance API client
│   │   ├── github_api.py         # GitHub API client
│   │   └── base_client.py        # Base API client class
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── portfolio.py          # Portfolio analysis
│   │   ├── risk_metrics.py       # Risk calculations
│   │   └── optimization.py      # Portfolio optimization
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   └── workflow.py          # API orchestration
│   └── utils/
│       ├── __init__.py
│       ├── data_processor.py    # Data transformation
│       └── cache.py             # Caching utilities
├── tests/
├── docs/
├── main.py                      # Main entry point
├── cli.py                       # CLI interface
├── api_server.py               # REST API server
├── requirements.txt
├── setup.py
├── .env.example
└── README.md
```

## 🔌 API Integrations

### 1. Alpha Vantage
- Real-time stock quotes
- Historical data
- Technical indicators
- Market sentiment

### 2. Yahoo Finance
- Market data
- Company information
- Financial statements

### 3. GitHub API
- Repository management
- Issue tracking
- Automated documentation

### 4. FRED (Federal Reserve)
- Economic indicators
- Interest rates
- Macroeconomic data

## 📊 Usage Examples

### Fetch Market Data

```python
from src.api_clients.alpha_vantage import AlphaVantageClient

client = AlphaVantageClient(api_key="your_key")
data = client.get_quote("AAPL")
print(data)
```

### Portfolio Analysis

```python
from src.analysis.portfolio import PortfolioAnalyzer

portfolio = PortfolioAnalyzer(symbols=["AAPL", "GOOGL", "MSFT"])
metrics = portfolio.calculate_risk_metrics()
print(metrics)
```

### API Orchestration

```python
from src.orchestrator.workflow import WorkflowOrchestrator

orchestrator = WorkflowOrchestrator()
results = orchestrator.run_analysis_workflow(
    symbols=["AAPL", "GOOGL"],
    risk_level="moderate"
)
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test
pytest tests/test_portfolio.py
```

## 📈 Build & Deploy

### Build

```bash
# Install build tools
pip install build

# Build package
python -m build

# Install locally
pip install -e .
```

### Docker (Optional)

```bash
docker build -t financial-api-demo .
docker run -p 8000:8000 financial-api-demo
```

## 📚 Documentation

- [API Reference](docs/API_REFERENCE.md)
- [Architecture Guide](docs/ARCHITECTURE.md)
- [API Integration Guide](docs/API_INTEGRATION.md)

## 🔒 Security

- API keys stored in `.env` (not committed)
- Rate limiting implemented
- Error handling and retries
- Input validation

## 📝 License

MIT License

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Built for Financial Engineering Demonstration**
