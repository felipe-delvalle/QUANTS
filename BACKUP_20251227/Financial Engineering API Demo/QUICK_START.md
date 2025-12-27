# 🚀 Quick Start Guide

## Installation (3 Steps)

### 1. Run Build Script
```bash
cd "Financial Engineering API Demo"
./build.sh
```

### 2. Configure API Keys
Edit `.env` file and add your API keys:
```env
ALPHA_VANTAGE_API_KEY=your_key_here
GITHUB_TOKEN=your_github_token
GITHUB_REPO=your_username/your_repo
```

### 3. Run Demo
```bash
# Activate virtual environment
source venv/bin/activate

# Run main demo
python main.py

# Or use CLI
python cli.py quote AAPL --source yahoo
```

## API Keys Needed

1. **Alpha Vantage** (Optional): https://www.alphavantage.co/support/#api-key
2. **GitHub Token** (Optional): https://github.com/settings/tokens
3. **Yahoo Finance**: No key needed (free)

## What Gets Demonstrated

✅ **Multi-API Integration**
- Alpha Vantage API (real-time quotes)
- Yahoo Finance API (market data)
- GitHub API (repository management)

✅ **Financial Analysis**
- Portfolio risk metrics (VaR, CVaR, Sharpe Ratio)
- Portfolio optimization
- Performance analysis

✅ **Workflow Orchestration**
- Coordinated API calls
- Automated workflows
- Error handling

## Project Structure

```
Financial Engineering API Demo/
├── src/
│   ├── api_clients/      # API integration clients
│   ├── analysis/         # Portfolio & risk analysis
│   └── orchestrator/     # Workflow management
├── main.py              # Main demo script
├── cli.py               # Command-line interface
├── build.sh             # Build script
└── requirements.txt     # Dependencies
```

## Example Usage

### Get Stock Quote
```python
from src.api_clients.yahoo_finance import YahooFinanceClient

client = YahooFinanceClient()
quote = client.get_quote("AAPL")
print(quote)
```

### Portfolio Analysis
```python
from src.analysis.portfolio import PortfolioAnalyzer
import pandas as pd

# Your price data
prices = pd.DataFrame({...})

portfolio = PortfolioAnalyzer(symbols=["AAPL", "GOOGL", "MSFT"])
analysis = portfolio.analyze_portfolio(prices)
print(analysis)
```

### GitHub Integration
```python
from src.api_clients.github_api import GitHubAPIClient

client = GitHubAPIClient(token="your_token")
repo_info = client.get_repository_info("owner/repo")
print(repo_info)
```

## Next Steps

1. ✅ Run `./build.sh` to set up
2. ✅ Add API keys to `.env`
3. ✅ Run `python main.py` to see demos
4. ✅ Explore `src/` directory for code examples
5. ✅ Check `README.md` for full documentation

---

**Ready to demonstrate financial engineering with multi-API integration!** 🎯
