---
name: Fix Analysis Modal Issues
overview: "Fix multiple issues in the Financial Engineering API modal: incorrect stop loss/entry/target calculations, slow/broken Technical Analysis chart loading, and Risk section display problems."
todos:
  - id: fix-variable-scope
    content: Fix 'recent_returns' variable scope bug in detailed_analyzer.py (move calculation outside conditional block)
    status: pending
  - id: debug-price-calculations
    content: Add logging to debug price_std calculation and verify stop loss/target formulas are producing correct values
    status: pending
  - id: fix-price-logic
    content: Fix stop loss and target calculation logic if formulas are incorrect
    status: pending
  - id: fix-chart-loading-backend
    content: Add error handling and logging to /api/historical/{symbol} endpoint
    status: pending
  - id: fix-chart-loading-frontend
    content: Improve chart loading error handling and add loading states in analysis_modal.js
    status: pending
  - id: fix-risk-display
    content: Fix Risk section display issues (CSS transforms, visual clarity)
    status: pending
  - id: test-all-fixes
    content: Test all fixes with AAPL and other symbols, verify calculations are realistic
    status: pending
  - id: commit-changes
    content: Commit all changes to git branch (with user approval)
    status: pending
---

# Fix Financial Engineering API Analysis Modal Issues

## Problem Summary

Based on the screenshots and code analysis, there are 3 critical issues:

1. **Stop Loss & Entry/Target Calculations** - AAPL at $136 showing stop loss of $229.59 (should be below current price for BUY signal), targets at $315.67 and $352.57 (unrealistic)
2. **Technical Analysis Tab** - Charts not loading ("Error loading data" message), extremely slow or completely broken
3. **Risk Section Display** - Visual issues with the risk meter/gauge display

## Root Causes Identified

### Issue 1: Price Calculation Bug in `detailed_analyzer.py`

**Location**: `src/analysis/detailed_analyzer.py` lines 63-107

**Problems**:

- Line 80 references `recent_returns` variable that's only defined conditionally on line 68 (inside an if/else block)
- This causes "cannot access local variable 'recent_returns' where it is not associated with a value" error
- Logic uses `price_std` (standard deviation) to calculate stop loss/targets, but the calculations appear reversed or using wrong multipliers

**Fix Strategy**:

1. Move `recent_returns` calculation outside the conditional block (line 68)
2. Ensure it's always defined before line 80
3. Review and fix the stop loss/target calculation logic:

   - For BUY signals: stop loss should be BELOW current price, targets ABOVE
   - For SELL signals: stop loss should be ABOVE current price, targets BELOW
   - Use more reasonable multipliers (currently using 2x, 1.5x, 3x, 5x std dev which may be too large)

### Issue 2: Technical Analysis Chart Loading

**Location**: Multiple files involved

- Frontend: `static/js/analysis_modal.js` lines 364-404 (`loadTechnicalChartData`)
- Backend: `api_service.py` lines 363-450 (`get_historical_data` endpoint)

**Potential causes to investigate**:

1. API endpoint `/api/historical/{symbol}` returning errors or slow responses
2. Frontend JavaScript errors preventing chart initialization
3. Data format mismatch between backend response and frontend expectations
4. CORS or network issues
5. Chart.js library not loading properly

**Fix Strategy**:

1. Add better error logging to backend endpoint
2. Add frontend console logging to track chart loading progress
3. Check data format compatibility (backend returns dict with dates as keys, frontend expects this format)
4. Verify Chart.js and chartjs-chart-financial libraries are loading
5. Add loading indicators and better error messages

### Issue 3: Risk Display Issues

**Location**:

- HTML: `templates/components/analysis_modal.html` lines 155-160 (risk gauge structure)
- CSS: Lines 560-602 (risk meter styling)
- JS: `static/js/analysis_modal.js` lines 680-693 (`updateRiskAnalysis`)

**Problems**:

- Risk meter visual display looks "odd" per user feedback
- Likely CSS positioning or transform issues with the gauge needle
- Risk meter is a semi-circle gauge that rotates based on risk score

**Fix Strategy**:

1. Review CSS for risk-gauge, risk-meter positioning
2. Fix transform calculations for the meter rotation
3. Ensure risk score is being calculated and passed correctly
4. Improve visual styling for better clarity

## Files to Modify

### Core Fixes:

1. **`src/analysis/detailed_analyzer.py`** - Fix variable scope bug and calculation logic
2. **`api_service.py`** - Add logging and error handling to `/api/historical/{symbol}` endpoint
3. **`static/js/analysis_modal.js`** - Add better error handling and logging for chart loading
4. **`templates/components/analysis_modal.html`** - Fix risk meter CSS/structure if needed

### Supporting Changes:

5. Add comprehensive logging throughout to help debug future issues
6. Consider caching improvements for faster chart loading

## Implementation Steps

1. **Fix Variable Scope Bug** (Priority 1)

   - Move `recent_returns` calculation to always execute before line 80
   - Test with sample data to ensure no NameError

2. **Fix Price Calculations** (Priority 1)

   - Review stop loss/target formulas for BUY/SELL/HOLD signals
   - Ensure stop loss is on correct side of current price
   - Use more conservative multipliers for realistic targets
   - Add validation to ensure calculated prices make sense

3. **Fix Technical Analysis Charts** (Priority 2)

   - Add detailed logging to track API request/response
   - Add loading states and error messages in UI
   - Verify data format compatibility
   - Test with multiple symbols (AAPL, crypto, forex)

4. **Fix Risk Display** (Priority 3)

   - Review and fix CSS transforms for risk meter
   - Improve visual clarity of the gauge
   - Ensure proper rotation calculations

5. **Testing**

   - Test with AAPL ($136 spot price) to verify stop loss is below price
   - Test with different signals (BUY/SELL/HOLD)
   - Test chart loading with slow network
   - Test risk meter display at different risk scores

6. **Git Workflow**

   - Create feature branch for fixes
   - Make commits after each major fix (with user approval)
   - Ensure all changes are tracked

## Key Code Locations

**Variable Scope Bug:**

```python
# Line 68 in detailed_analyzer.py - this is INSIDE an if/else block
recent_returns = returns.tail(20).mean() if len(returns) >= 20 else returns.mean()

# Line 80 references it OUTSIDE the block - ERROR!
trend_strength = abs(recent_returns) if len(returns) >= 20 else 0.5
```

**Fix: Move line 68 calculation before line 64 (before the if statement)**

**Price Calculation Example (lines 89-107):**

Currently for BUY signal:

- Stop loss: `current_price - price_std * 2` ✓ (correct - below price)
- Target1: `current_price + price_std * 1.5` ✓ (correct - above price)
- Target2: `current_price + price_std * 3` ✓ (correct - above price)

The logic LOOKS correct, so the issue might be:

1. `price_std` is too large (need to check calculation)
2. The signal_type is being passed incorrectly
3. There's a calculation error elsewhere

**Need to verify**: Where is the $229 stop loss coming from if the formula looks correct?

## Questions to Resolve

1. Is the price data correct? (Is AAPL really $136?)
2. What is the actual value of `price_std` being calculated?
3. Is `signal_type` being passed correctly from frontend to backend?
4. Are there any other calculation bugs in the chain?