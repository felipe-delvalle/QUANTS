// Analysis Modal JavaScript Functions

// Global variables for chart instances
let priceChart = null;
let volumeProfileChart = null;
let historicalChart = null;

// Store current symbol for chart updates
let currentSymbol = null;

// Chart data cache
const chartDataCache = new Map();

// Show analysis modal for a symbol
function showAnalysisModal(symbol, data, signalType = null) {
  const logger = window.clientLogger || { info: () => {}, error: () => {}, debug: () => {}, warn: () => {} };
  
  logger.info('modal', 'showAnalysisModal_called', {
    symbol: symbol,
    signal_type: signalType,
    current_price: data.current_price,
    price_change: data.price_change
  });
  
  // Verify modal exists
  const modal = document.getElementById('analysisModal');
  if (!modal) {
    logger.error('modal', 'modal_element_not_found', {
      symbol: symbol,
      message: 'Analysis modal element not found in DOM'
    });
    alert('Analysis modal not available. Please refresh the page.');
    return;
  }
  
  logger.debug('modal', 'modal_element_found', {
    symbol: symbol,
    modal_display: modal.style.display,
    modal_class: modal.className
  });
  
  currentSymbol = symbol;
  
  // Update modal header
  const modalSymbol = document.getElementById('modalSymbol');
  const modalPrice = document.getElementById('modalPrice');
  const modalChange = document.getElementById('modalChange');
  
  const headerElements = {
    modalSymbol: !!modalSymbol,
    modalPrice: !!modalPrice,
    modalChange: !!modalChange
  };
  
  logger.debug('modal', 'header_elements_check', {
    symbol: symbol,
    elements_found: headerElements
  });
  
  if (modalSymbol) modalSymbol.textContent = symbol;
  if (modalPrice) modalPrice.textContent = `$${data.current_price.toFixed(2)}`;
  
  // Handle price change (may be 0 initially, will be updated from API)
  const changeClass = data.price_change > 0 ? 'positive' : (data.price_change < 0 ? 'negative' : '');
  if (modalChange) {
    modalChange.className = `price-change ${changeClass}`;
    if (data.price_change !== 0) {
      modalChange.textContent = `${data.price_change > 0 ? '+' : ''}${data.price_change.toFixed(1)}%`;
    } else {
      modalChange.textContent = 'Loading...';
    }
  }
  
  logger.info('modal', 'fetching_detailed_analysis', {
    symbol: symbol,
    signal_type: signalType
  });
  
  // Fetch detailed analysis
  fetchDetailedAnalysis(symbol, signalType).then(analysis => {
    logger.info('modal', 'analysis_fetched_successfully', {
      symbol: symbol,
      has_recommendation: !!analysis.recommendation,
      has_technical: !!analysis.technical_analysis,
      has_risk: !!analysis.risk_analysis
    });
    
    updateModalContent(analysis);
    
    // Update price and price change from analysis if available
    if (analysis.current_price) {
      // Update the displayed price with the real-time price from analysis
      if (modalPrice) {
        modalPrice.textContent = `$${analysis.current_price.toFixed(2)}`;
        logger.info('modal', 'price_updated_from_analysis', {
          symbol: symbol,
          old_price: data.current_price,
          new_price: analysis.current_price
        });
      }
      
      // Update price change if available
      if (modalChange) {
        // Calculate change if we have previous price data, otherwise keep loading state
        const changeText = modalChange.textContent;
        if (changeText === 'Loading...' && analysis.recommendation) {
          // Use a default or calculate from historical if available
          modalChange.textContent = '0.0%';
        }
      }
    }
    
    // Pre-load charts for the active tab
    const activeTab = document.querySelector('.tab-content.active');
    if (activeTab) {
      logger.debug('modal', 'preloading_charts', {
        symbol: symbol,
        active_tab: activeTab.id
      });
      
      if (activeTab.id === 'technicalTab') {
        if (!priceChart) {
          initializeTechnicalCharts();
        }
        loadTechnicalChartData(symbol);
      } else if (activeTab.id === 'historicalTab') {
        if (!historicalChart) {
          initializeHistoricalChart();
        }
        loadHistoricalChartData(symbol);
      }
    }
  }).catch(error => {
    logger.error('modal', 'analysis_fetch_failed', {
      symbol: symbol,
      error_message: error.message,
      error_stack: error.stack
    }, error);
    // Still show modal even if analysis fetch fails
  });
  
  // Show modal
  logger.info('modal', 'displaying_modal', {
    symbol: symbol,
    modal_display_before: modal.style.display
  });
  
  modal.style.display = 'block';
  
  logger.info('modal', 'modal_displayed', {
    symbol: symbol,
    modal_display_after: modal.style.display,
    modal_visible: modal.offsetParent !== null
  });
}

// Close analysis modal
function closeAnalysisModal() {
  document.getElementById('analysisModal').style.display = 'none';
  
  // Destroy charts to free memory
  if (priceChart) {
    priceChart.destroy();
    priceChart = null;
  }
  if (volumeProfileChart) {
    volumeProfileChart.destroy();
    volumeProfileChart = null;
  }
  if (historicalChart) {
    historicalChart.destroy();
    historicalChart = null;
  }
}

// Switch between tabs
function switchTab(tabName) {
  // Hide all tabs
  document.querySelectorAll('.tab-content').forEach(tab => {
    tab.classList.remove('active');
  });
  
  // Remove active from all buttons
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Show selected tab
  document.getElementById(`${tabName}Tab`).classList.add('active');
  
  // Mark button as active
  event.target.classList.add('active');
  
  // Initialize charts if needed and load data
  if (tabName === 'technical') {
    if (!priceChart) {
      initializeTechnicalCharts();
    }
    if (currentSymbol) {
      loadTechnicalChartData(currentSymbol);
    }
  } else if (tabName === 'historical') {
    if (!historicalChart) {
      initializeHistoricalChart();
    }
    if (currentSymbol) {
      loadHistoricalChartData(currentSymbol);
    }
  }
}

// Fetch detailed analysis from API
async function fetchDetailedAnalysis(symbol, signalType = null) {
  try {
    const url = signalType ? `/api/analysis/${symbol}?signal_type=${signalType}` : `/api/analysis/${symbol}`;
    const response = await fetch(url);
    if (!response.ok) throw new Error('Failed to fetch analysis');
    return await response.json();
  } catch (error) {
    console.error('Error fetching analysis:', error);
    // Return mock data for now
    return generateMockAnalysis(symbol);
  }
}

// Update modal content with analysis data
function updateModalContent(analysis) {
  try {
    // Update overview tab
    if (analysis.recommendation) {
      updateOverviewTab(analysis.recommendation);
    }
    
    // Update technical indicators
    if (analysis.technical_analysis) {
      updateTechnicalIndicators(analysis.technical_analysis);
    }
    
    // Update risk analysis
    if (analysis.risk_analysis) {
      updateRiskAnalysis(analysis.risk_analysis);
    }
    
    // Update historical performance
    if (analysis.historical_performance) {
      updateHistoricalPerformance(analysis.historical_performance);
    }
  } catch (error) {
    console.error('Error updating modal content:', error);
    const logger = window.clientLogger || { error: () => {} };
    logger.error('modal', 'update_modal_content_error', {
      error: error.message,
      analysis_keys: analysis ? Object.keys(analysis) : []
    });
  }
}

// Update overview tab
function updateOverviewTab(recommendation) {
  try {
    if (!recommendation) {
      console.warn('Recommendation data missing');
      return;
    }
    
    // Recommendation
    const rating = document.getElementById('recRating');
    if (rating && recommendation.recommendation) {
      rating.textContent = recommendation.recommendation;
      rating.className = `rec-rating ${recommendation.action === 'BUY' ? 'positive' : recommendation.action === 'SELL' ? 'negative' : ''}`;
    }
    
    // Confidence
    if (recommendation.confidence !== undefined) {
      const confidence = recommendation.confidence * 100;
      const confidenceFill = document.getElementById('confidenceFill');
      const confidenceValue = document.getElementById('confidenceValue');
      if (confidenceFill) {
        confidenceFill.style.width = `${confidence}%`;
      }
      if (confidenceValue) {
        confidenceValue.textContent = `${confidence.toFixed(0)}%`;
      }
    }
    
    // Entry and targets
    const entryRange = document.getElementById('entryRange');
    const stopLoss = document.getElementById('stopLoss');
    const target1 = document.getElementById('target1');
    const target2 = document.getElementById('target2');
    
    if (entryRange && recommendation.entry_range) {
      entryRange.textContent = recommendation.entry_range;
    }
    if (stopLoss && recommendation.stop_loss) {
      stopLoss.textContent = recommendation.stop_loss;
    }
    if (target1 && recommendation.targets && recommendation.targets[0]) {
      target1.textContent = recommendation.targets[0];
    }
    if (target2 && recommendation.targets && recommendation.targets[1]) {
      target2.textContent = recommendation.targets[1];
    }
    
    // Professional analysis text
    const analysisTextEl = document.getElementById('analysisText');
    if (analysisTextEl) {
      try {
        const analysisText = generateProfessionalAnalysis(recommendation);
        analysisTextEl.textContent = analysisText;
      } catch (genError) {
        console.error('Error generating analysis text:', genError);
        analysisTextEl.textContent = 'Analysis data available.';
      }
    }
  } catch (error) {
    console.error('Error updating overview tab:', error);
  }
}

// Update technical indicators
function updateTechnicalIndicators(technical) {
  try {
    if (!technical || !technical.indicators) {
      console.warn('Technical analysis data missing or incomplete');
      return;
    }
    
    // RSI
    if (technical.indicators.rsi) {
      const rsiValue = document.getElementById('rsiValue');
      const rsiSignal = document.getElementById('rsiSignal');
      if (rsiValue) {
        rsiValue.textContent = technical.indicators.rsi.value.toFixed(1);
      }
      if (rsiSignal) {
        rsiSignal.textContent = technical.indicators.rsi.signal;
        rsiSignal.className = `signal ${technical.indicators.rsi.signal === 'oversold' ? 'positive' : technical.indicators.rsi.signal === 'overbought' ? 'negative' : ''}`;
      }
    }
    
    // MACD
    if (technical.indicators.macd) {
      const macdValue = document.getElementById('macdValue');
      const macdSignal = document.getElementById('macdSignal');
      if (macdValue) {
        macdValue.textContent = technical.indicators.macd.signal;
      }
      if (macdSignal) {
        macdSignal.className = `signal ${technical.indicators.macd.signal === 'bullish' ? 'positive' : 'negative'}`;
      }
    }
  } catch (error) {
    console.error('Error updating technical indicators:', error);
  }
}

// Initialize technical charts
function initializeTechnicalCharts() {
  // Price chart - use line chart instead of candlestick (Chart.js doesn't have built-in candlestick)
  const priceCtx = document.getElementById('priceChart').getContext('2d');
  priceChart = new Chart(priceCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Price',
          data: [],
          borderColor: '#5de0e6',
          backgroundColor: 'rgba(93, 224, 230, 0.1)',
          fill: true,
          tension: 0.1
        },
        {
          label: 'SMA 20',
          data: [],
          borderColor: '#ffa500',
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderDash: [5, 5],
          pointRadius: 0
        },
        {
          label: 'SMA 50',
          data: [],
          borderColor: '#ff0000',
          backgroundColor: 'transparent',
          borderWidth: 1,
          borderDash: [5, 5],
          pointRadius: 0
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { 
          display: true,
          position: 'top'
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Date'
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: 'Price ($)'
          }
        }
      }
    }
  });
  
  // Volume profile
  const vpCtx = document.getElementById('volumeProfile').getContext('2d');
  volumeProfileChart = new Chart(vpCtx, {
    type: 'bar',
    data: {
      labels: [],
      datasets: [{
        label: 'Volume',
        data: [],
        backgroundColor: 'rgba(93, 224, 230, 0.5)'
      }]
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: 'Volume'
          }
        }
      }
    }
  });
}

// Load technical chart data
async function loadTechnicalChartData(symbol) {
  // Check cache first
  if (chartDataCache.has(symbol)) {
    const cachedData = chartDataCache.get(symbol);
    updateChartWithData(cachedData, symbol);
    return;
  }
  
  // Show loading indicator
  if (priceChart) {
    priceChart.data.labels = ['Loading...'];
    priceChart.data.datasets[0].data = [0];
    priceChart.update();
  }
  
  try {
    const response = await fetch(`/api/historical/${symbol}?period=1y&indicators=true`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // Cache the data
    chartDataCache.set(symbol, data);
    
    if (data.prices && priceChart) {
      updateChartWithData(data, symbol);
    } else {
      throw new Error('Invalid data format: missing prices');
    }
  } catch (error) {
    console.error('Error loading technical chart data:', error);
    // Show error message on chart
    if (priceChart) {
      priceChart.data.labels = ['Error loading data'];
      priceChart.data.datasets[0].data = [0];
      priceChart.update();
    }
  }
}

// Helper function to update chart with data
function updateChartWithData(data, symbol) {
  if (!priceChart) return;
  
  try {
    // Convert prices object to arrays, sorted by date
    const dates = Object.keys(data.prices).sort();
    const prices = dates.map(d => {
      const priceData = data.prices[d];
      if (typeof priceData === 'object' && priceData.close) {
        return parseFloat(priceData.close) || 0;
      }
      return parseFloat(priceData) || 0;
    });
    const volumes = dates.map(d => {
      const priceData = data.prices[d];
      if (typeof priceData === 'object' && priceData.volume) {
        return parseFloat(priceData.volume) || 0;
      }
      return 0;
    });
    
    // Update price chart
    priceChart.data.labels = dates.map(d => {
      try {
        // Try parsing as ISO date string or timestamp
        const date = new Date(d);
        if (isNaN(date.getTime())) {
          // If parsing fails, try as timestamp
          const timestamp = parseInt(d);
          if (!isNaN(timestamp)) {
            return new Date(timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
          }
          return d;
        }
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
      } catch {
        return d;
      }
    });
    priceChart.data.datasets[0].data = prices;
    priceChart.data.datasets[0].label = `${symbol} Price`;
    
    // Add moving averages if available - align with price dates
    if (data.indicators && data.indicators.sma_20 && Object.keys(data.indicators.sma_20).length > 0) {
      const sma20Aligned = dates.map(d => {
        const value = data.indicators.sma_20[d];
        return value !== undefined && value !== null ? parseFloat(value) : null;
      });
      priceChart.data.datasets[1].data = sma20Aligned;
      priceChart.data.datasets[1].label = 'SMA 20';
    }
    
    if (data.indicators && data.indicators.sma_50 && Object.keys(data.indicators.sma_50).length > 0) {
      const sma50Aligned = dates.map(d => {
        const value = data.indicators.sma_50[d];
        return value !== undefined && value !== null ? parseFloat(value) : null;
      });
      priceChart.data.datasets[2].data = sma50Aligned;
      priceChart.data.datasets[2].label = 'SMA 50';
    }
    
    priceChart.update();
    
    // Update volume profile (simplified - show recent volumes)
    if (volumeProfileChart && volumes.length > 0) {
      // Take last 20 data points for volume profile
      const recentVolumes = volumes.slice(-20);
      const recentDates = dates.slice(-20).map(d => {
        try {
          const date = new Date(d);
          if (isNaN(date.getTime())) {
            const timestamp = parseInt(d);
            if (!isNaN(timestamp)) {
              return new Date(timestamp).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }
            return d;
          }
          return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        } catch {
          return d;
        }
      });
      
      volumeProfileChart.data.labels = recentDates;
      volumeProfileChart.data.datasets[0].data = recentVolumes;
      volumeProfileChart.update();
    }
  } catch (error) {
    console.error('Error updating chart:', error);
    if (priceChart) {
      priceChart.data.labels = ['Error processing data'];
      priceChart.data.datasets[0].data = [0];
      priceChart.update();
    }
  }
}

// Initialize historical chart
function initializeHistoricalChart() {
  const ctx = document.getElementById('historicalChart').getContext('2d');
  historicalChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {
          label: 'Price',
          data: [],
          borderColor: '#5de0e6',
          backgroundColor: 'rgba(93, 224, 230, 0.1)',
          fill: true,
          tension: 0.1
        },
        {
          label: 'Buy Signals',
          data: [],
          type: 'scatter',
          borderColor: '#6be07b',
          backgroundColor: '#6be07b',
          pointRadius: 6,
          pointHoverRadius: 8
        },
        {
          label: 'Sell Signals',
          data: [],
          type: 'scatter',
          borderColor: '#ff7b7b',
          backgroundColor: '#ff7b7b',
          pointRadius: 6,
          pointHoverRadius: 8
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          mode: 'index',
          intersect: false
        }
      },
      scales: {
        x: {
          display: true,
          title: {
            display: true,
            text: 'Date'
          }
        },
        y: {
          display: true,
          title: {
            display: true,
            text: 'Price ($)'
          }
        }
      }
    }
  });
}

// Load historical chart data
async function loadHistoricalChartData(symbol, timeframe = '1Y') {
  try {
    const periodMap = {
      '1M': '1mo',
      '3M': '3mo',
      '6M': '6mo',
      '1Y': '1y',
      '5Y': '5y'
    };
    
    const period = periodMap[timeframe] || '1y';
    const response = await fetch(`/api/historical/${symbol}?period=${period}&indicators=true`);
    if (!response.ok) throw new Error('Failed to fetch historical data');
    
    const data = await response.json();
    
    if (data.prices && historicalChart) {
      // Convert prices object to arrays, sorted by date
      const dates = Object.keys(data.prices).sort();
      const prices = dates.map(d => parseFloat(data.prices[d].close) || 0);
      
      // Update price line
      historicalChart.data.labels = dates.map(d => {
        try {
          return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        } catch {
          return d;
        }
      });
      historicalChart.data.datasets[0].data = prices;
      historicalChart.data.datasets[0].label = `${symbol} Price`;
      
      // Add signal history if available
      if (data.signal_history && Array.isArray(data.signal_history) && data.signal_history.length > 0) {
        const buySignals = [];
        const sellSignals = [];
        
        data.signal_history.forEach(signal => {
          try {
            const signalDate = new Date(signal.date);
            const dateStr = signalDate.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            const dateIndex = dates.findIndex(d => {
              try {
                return new Date(d).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) === dateStr;
              } catch {
                return false;
              }
            });
            
            if (dateIndex >= 0 && dateIndex < prices.length) {
              const price = signal.price || prices[dateIndex];
              
              if (signal.signal === 'BUY' || signal.signal === 'buy') {
                buySignals.push({ x: dateIndex, y: price });
              } else if (signal.signal === 'SELL' || signal.signal === 'sell') {
                sellSignals.push({ x: dateIndex, y: price });
              }
            }
          } catch (e) {
            // Skip invalid signals
            console.warn('Invalid signal data:', signal, e);
          }
        });
        
        // Convert to Chart.js format (array of values at specific indices)
        const buyData = new Array(prices.length).fill(null);
        const sellData = new Array(prices.length).fill(null);
        
        buySignals.forEach(s => {
          if (s.x >= 0 && s.x < buyData.length) {
            buyData[s.x] = s.y;
          }
        });
        
        sellSignals.forEach(s => {
          if (s.x >= 0 && s.x < sellData.length) {
            sellData[s.x] = s.y;
          }
        });
        
        historicalChart.data.datasets[1].data = buyData;
        historicalChart.data.datasets[2].data = sellData;
      } else {
        // Clear signals if no data
        historicalChart.data.datasets[1].data = [];
        historicalChart.data.datasets[2].data = [];
      }
      
      historicalChart.update();
    }
  } catch (error) {
    console.error('Error loading historical chart data:', error);
    // Show error message on chart
    if (historicalChart) {
      historicalChart.data.labels = ['Error loading data'];
      historicalChart.data.datasets[0].data = [0];
      historicalChart.update();
    }
  }
}

// Update risk analysis
function updateRiskAnalysis(risk) {
  // Risk score and meter
  const riskScore = risk.risk_score;
  document.getElementById('riskValue').textContent = (riskScore * 10).toFixed(1);
  document.getElementById('riskRating').textContent = risk.risk_rating;
  
  // Rotate risk meter based on score
  const rotation = -90 + (riskScore * 180);
  document.getElementById('riskMeter').style.transform = `rotate(${rotation}deg)`;
  
  // Risk metrics
  document.getElementById('annualVol').textContent = `${(risk.volatility.annual * 100).toFixed(1)}%`;
  document.getElementById('maxDrawdown').textContent = `${(risk.max_drawdown * 100).toFixed(1)}%`;
}

// Generate professional analysis text
function generateProfessionalAnalysis(recommendation) {
  const templates = [
    `Based on comprehensive technical and quantitative analysis, ${recommendation.symbol} exhibits ${recommendation.trend} characteristics with a confidence level of ${(recommendation.confidence * 100).toFixed(0)}%. The current market structure suggests ${recommendation.timeframe} outlook with entry opportunities in the ${recommendation.entry_range} range. Key resistance levels are identified at ${recommendation.targets[0]} and ${recommendation.targets[1]}, while risk management suggests a stop loss at ${recommendation.stop_loss}.`,
    
    `Technical indicators are signaling a ${recommendation.action.toLowerCase()} opportunity with ${(recommendation.confidence * 100).toFixed(0)}% confidence. The risk/reward ratio of ${recommendation.risk_reward_ratio} presents an attractive setup for ${recommendation.timeframe} traders. Volume analysis confirms institutional accumulation patterns, supporting the bullish thesis.`,
    
    `Market structure analysis reveals ${recommendation.trend} momentum with key support established at recent lows. The FDV Momentum Score indicates robust strength, while smart money flow suggests institutional positioning aligns with our ${recommendation.action.toLowerCase()} recommendation. Entry within the ${recommendation.entry_range} range offers optimal risk/reward characteristics.`
  ];
  
  return templates[Math.floor(Math.random() * templates.length)];
}

// Update timeframe for historical chart
function updateTimeframe(timeframe) {
  // Update active button
  document.querySelectorAll('.tf-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  event.target.classList.add('active');
  
  // Reload chart with new timeframe
  if (currentSymbol && historicalChart) {
    loadHistoricalChartData(currentSymbol, timeframe);
  }
}

// Update historical performance
function updateHistoricalPerformance(performance) {
  // This would update the performance table with actual data
  // For now, using the static HTML content
}

// Action button functions
async function executeAnalysis() {
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/29801ca5-7500-4362-b277-1cf75bd27ca2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analysis_modal.js:729',message:'executeAnalysis_entry',data:{timestamp:Date.now()},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  // #endregion agent log
  const symbol = document.getElementById('modalSymbol').textContent;
  const signal = document.getElementById('recRating').textContent.trim();
  
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/29801ca5-7500-4362-b277-1cf75bd27ca2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analysis_modal.js:733',message:'before_fetch_request',data:{symbol:symbol,signal:signal,url:signal?`/api/report/${symbol}?signal_type=${signal}`:`/api/report/${symbol}`},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
  // #endregion agent log
  
  // Show loading notification
  showNotification('Generating PDF report...', 'info');
  
  try {
    const url = signal ? `/api/report/${symbol}?signal_type=${signal}` : `/api/report/${symbol}`;
    const response = await fetch(url);
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/29801ca5-7500-4362-b277-1cf75bd27ca2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analysis_modal.js:741',message:'after_fetch_response',data:{symbol:symbol,status:response.status,statusText:response.statusText,ok:response.ok},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion agent log
    
    if (!response.ok) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/29801ca5-7500-4362-b277-1cf75bd27ca2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analysis_modal.js:744',message:'response_not_ok',data:{symbol:symbol,status:response.status,statusText:response.statusText},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
      // #endregion agent log
      const error = await response.json();
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/29801ca5-7500-4362-b277-1cf75bd27ca2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analysis_modal.js:747',message:'error_response_parsed',data:{symbol:symbol,error_detail:error.detail},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
      // #endregion agent log
      throw new Error(error.detail || 'Failed to generate report');
    }
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/29801ca5-7500-4362-b277-1cf75bd27ca2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analysis_modal.js:752',message:'before_blob_conversion',data:{symbol:symbol},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion agent log
    
    // Get the PDF blob
    const blob = await response.blob();
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/29801ca5-7500-4362-b277-1cf75bd27ca2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analysis_modal.js:756',message:'after_blob_conversion',data:{symbol:symbol,blob_size:blob.size,blob_type:blob.type},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion agent log
    
    // Create download link
    const url_obj = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url_obj;
    a.download = `${symbol}_analysis_report.pdf`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url_obj);
    
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/29801ca5-7500-4362-b277-1cf75bd27ca2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analysis_modal.js:767',message:'download_triggered',data:{symbol:symbol},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion agent log
    
    showNotification('PDF report downloaded!', 'success');
  } catch (error) {
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/29801ca5-7500-4362-b277-1cf75bd27ca2',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'analysis_modal.js:771',message:'catch_block_executed',data:{symbol:symbol,error_message:error.message,error_name:error.name},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion agent log
    console.error('Error generating report:', error);
    showNotification(`Failed to generate report: ${error.message}`, 'error');
  }
}

async function addToWatchlist() {
  const symbol = document.getElementById('modalSymbol').textContent;
  
  try {
    const response = await fetch(`/api/watchlist?symbol=${symbol}`, {
      method: 'POST'
    });
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to add to watchlist');
    }
    
    const result = await response.json();
    
    if (result.status === 'success') {
      showNotification(`${symbol} added to watchlist!`, 'success');
    } else if (result.status === 'exists') {
      showNotification(`${symbol} is already in watchlist`, 'info');
    } else {
      showNotification(result.message || 'Added to watchlist', 'success');
    }
  } catch (error) {
    console.error('Error adding to watchlist:', error);
    showNotification(`Failed to add ${symbol} to watchlist: ${error.message}`, 'error');
  }
}

function shareAnalysis() {
  const symbol = document.getElementById('modalSymbol').textContent;
  const shareUrl = `${window.location.origin}/analysis/${symbol}?share=true`;
  
  // Try modern clipboard API first
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(shareUrl).then(() => {
      showNotification('Link copied to clipboard!', 'success');
    }).catch(err => {
      console.error('Failed to copy:', err);
      fallbackCopy(shareUrl);
    });
  } else {
    fallbackCopy(shareUrl);
  }
}

function fallbackCopy(text) {
  const textArea = document.createElement('textarea');
  textArea.value = text;
  textArea.style.position = 'fixed';
  textArea.style.left = '-999999px';
  document.body.appendChild(textArea);
  textArea.select();
  try {
    document.execCommand('copy');
    showNotification('Link copied to clipboard!', 'success');
  } catch (err) {
    console.error('Fallback copy failed:', err);
    showNotification('Failed to copy link. Please copy manually: ' + text, 'error');
  }
  document.body.removeChild(textArea);
}

function showNotification(message, type = 'info') {
  // Create notification element
  const notification = document.createElement('div');
  notification.className = `notification ${type}`;
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${type === 'success' ? '#6be07b' : type === 'error' ? '#ff7b7b' : '#5de0e6'};
    color: #0b1221;
    padding: 12px 20px;
    border-radius: 4px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    z-index: 10000;
    animation: slideIn 0.3s ease-out;
  `;
  
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.style.animation = 'slideOut 0.3s ease-out';
    setTimeout(() => {
      document.body.removeChild(notification);
    }, 300);
  }, 3000);
}

// Generate mock analysis data (for demo)
function generateMockAnalysis(symbol) {
  return {
    symbol: symbol,
    recommendation: {
      recommendation: "Buy",
      action: "BUY",
      confidence: 0.75,
      timeframe: "3-6 months",
      entry_range: "$148-152",
      stop_loss: "$142",
      targets: ["$160", "$165", "$170"],
      risk_reward_ratio: 2.5,
      trend: "bullish"
    },
    technical_analysis: {
      indicators: {
        rsi: { value: 65, signal: "neutral" },
        macd: { signal: "bullish" }
      },
      trend: "uptrend"
    },
    risk_analysis: {
      risk_score: 0.32,
      risk_rating: "Medium Risk",
      volatility: { annual: 0.245 },
      max_drawdown: -0.183
    },
    historical_performance: {}
  };
}

// Add click handlers to opportunity rows
// Make addClickHandlers globally accessible so it can be called after table updates
window.addClickHandlers = function() {
  const logger = window.clientLogger || { info: () => {}, error: () => {}, debug: () => {} };
  
  logger.info('click_handler', 'addClickHandlers_called', {
    timestamp: new Date().toISOString()
  });
  
  // Log table state
  const resultsTable = document.getElementById('resultsTable');
  const resultsRows = resultsTable ? document.querySelectorAll('#resultsTable tbody tr') : [];
  const strategyRows = document.querySelectorAll('.strategy-table tbody tr');
  
  logger.debug('click_handler', 'table_state', {
    results_table_exists: !!resultsTable,
    results_rows_count: resultsRows.length,
    strategy_rows_count: strategyRows.length
  });
  
  // Handle main results table
  let resultsHandlersAttached = 0;
  resultsRows.forEach((row, index) => {
    // Skip if already has click handler (check for data attribute)
    if (row.dataset.hasClickHandler === 'true') {
      logger.debug('click_handler', 'handler_already_attached', {
        table: 'resultsTable',
        row_index: index,
        symbol: row.cells[0]?.textContent?.trim()
      });
      return;
    }
    
    row.style.cursor = 'pointer';
    row.dataset.hasClickHandler = 'true'; // Mark as having handler
    
    row.addEventListener('click', function(e) {
      try {
        logger.info('click_handler', 'row_clicked', {
          table: 'resultsTable',
          row_index: index,
          cell_count: this.cells.length
        });
        
        // Prevent event bubbling
        e.stopPropagation();
        
        // Get data from table columns
        // Column 0: Symbol, 1: Asset, 2: Signal, 3: Confidence, 4: Price, 5: Trend, 6: Reasons
        const symbol = this.cells[0]?.textContent?.trim();
        if (!symbol) {
          logger.error('click_handler', 'no_symbol_found', {
            row_index: index,
            cell_0_content: this.cells[0]?.textContent
          });
          return;
        }
        
        const signal = this.cells[2]?.textContent?.trim() || 'BUY';
        const priceText = this.cells[4]?.textContent?.replace('$', '').replace(',', '') || '0';
        const price = parseFloat(priceText);
        
        logger.debug('click_handler', 'data_extracted', {
          symbol: symbol,
          signal: signal,
          price_text: priceText,
          price_parsed: price,
          row_index: index
        });
        
        if (isNaN(price) || price <= 0) {
          logger.error('click_handler', 'invalid_price', {
            symbol: symbol,
            price_text: priceText,
            price_parsed: price
          });
          return;
        }
        
        // Price change not available in table - will be calculated from API data
        // Use 0 as default, will be updated when analysis loads
        logger.info('click_handler', 'calling_showAnalysisModal', {
          symbol: symbol,
          signal: signal,
          price: price
        });
        
        showAnalysisModal(symbol, {
          current_price: price,
          price_change: 0  // Temporary, will be updated from API response
        }, signal);
      } catch (error) {
        logger.error('click_handler', 'click_handler_error', {
          row_index: index,
          error_message: error.message,
          error_stack: error.stack
        }, error);
        alert('Error opening analysis. Please check the browser console for details.');
      }
    });
    
    resultsHandlersAttached++;
  });
  
  logger.info('click_handler', 'results_handlers_attached', {
    count: resultsHandlersAttached
  });
  
  // Handle strategy tables (on_sale and overbought sections)
  let strategyHandlersAttached = 0;
  strategyRows.forEach((row, index) => {
    // Skip if already has click handler
    if (row.dataset.hasClickHandler === 'true') {
      logger.debug('click_handler', 'strategy_handler_already_attached', {
        row_index: index,
        symbol: row.cells[0]?.textContent?.trim()
      });
      return;
    }
    
    row.style.cursor = 'pointer';
    row.dataset.hasClickHandler = 'true';
    
    row.addEventListener('click', function(e) {
      try {
        logger.info('click_handler', 'strategy_row_clicked', {
          row_index: index,
          cell_count: this.cells.length
        });
        
        e.stopPropagation();
        
        // Strategy table columns: 0: Symbol, 1: Asset, 2: Price, 3: Confidence, 4: Reasons
        const symbol = this.cells[0]?.textContent?.trim();
        if (!symbol) {
          logger.error('click_handler', 'no_symbol_in_strategy_row', {
            row_index: index,
            cell_0_content: this.cells[0]?.textContent
          });
          return;
        }
        
        // Determine signal based on which table (on_sale = BUY, overbought = SELL)
        const table = this.closest('.strategy-table');
        const section = table?.closest('.strategy-section');
        const isOverbought = section?.querySelector('.overbought-header') !== null;
        const signal = isOverbought ? 'SELL' : 'BUY';
        
        logger.debug('click_handler', 'strategy_signal_determined', {
          symbol: symbol,
          is_overbought: isOverbought,
          signal: signal
        });
        
        const priceText = this.cells[2]?.textContent?.replace('$', '').replace(',', '') || '0';
        const price = parseFloat(priceText);
        
        if (isNaN(price) || price <= 0) {
          logger.error('click_handler', 'invalid_price_strategy', {
            symbol: symbol,
            price_text: priceText,
            price_parsed: price
          });
          return;
        }
        
        logger.info('click_handler', 'calling_showAnalysisModal_strategy', {
          symbol: symbol,
          signal: signal,
          price: price
        });
        
        showAnalysisModal(symbol, {
          current_price: price,
          price_change: 0
        }, signal);
      } catch (error) {
        logger.error('click_handler', 'strategy_click_handler_error', {
          row_index: index,
          error_message: error.message,
          error_stack: error.stack
        }, error);
        alert('Error opening analysis. Please check the browser console for details.');
      }
    });
    
    strategyHandlersAttached++;
  });
  
  logger.info('click_handler', 'strategy_handlers_attached', {
    count: strategyHandlersAttached
  });
};

document.addEventListener('DOMContentLoaded', function() {
  const logger = window.clientLogger || { info: () => {}, error: () => {}, debug: () => {} };
  
  logger.info('mutation_observer', 'DOMContentLoaded', {
    timestamp: new Date().toISOString()
  });
  
  // Check if modal exists
  const modal = document.getElementById('analysisModal');
  logger.debug('mutation_observer', 'modal_check_on_load', {
    modal_exists: !!modal,
    modal_display: modal ? modal.style.display : 'N/A'
  });
  
  // Check table state
  const resultsTable = document.getElementById('resultsTable');
  logger.debug('mutation_observer', 'table_check_on_load', {
    results_table_exists: !!resultsTable,
    table_rows: resultsTable ? document.querySelectorAll('#resultsTable tbody tr').length : 0
  });
  
  // Add handlers initially
  if (typeof window.addClickHandlers === 'function') {
    logger.info('mutation_observer', 'calling_addClickHandlers_initial', {});
    window.addClickHandlers();
  } else {
    logger.error('mutation_observer', 'addClickHandlers_not_available', {});
  }
  
  // Re-add handlers when table updates via MutationObserver
  const observer = new MutationObserver(function(mutations) {
    mutations.forEach(function(mutation) {
      if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
        logger.debug('mutation_observer', 'table_mutation_detected', {
          added_nodes: mutation.addedNodes.length,
          removed_nodes: mutation.removedNodes.length
        });
        
        // Small delay to ensure DOM is fully updated
        setTimeout(function() {
          if (typeof window.addClickHandlers === 'function') {
            logger.info('mutation_observer', 'calling_addClickHandlers_after_mutation', {});
            window.addClickHandlers();
          } else {
            logger.error('mutation_observer', 'addClickHandlers_not_available_after_mutation', {});
          }
        }, 50);
      }
    });
  });
  
  if (resultsTable) {
    observer.observe(resultsTable, { 
      childList: true, 
      subtree: true 
    });
    logger.info('mutation_observer', 'observer_attached', {
      target: 'resultsTable'
    });
  } else {
    logger.warn('mutation_observer', 'resultsTable_not_found', {});
  }
});
