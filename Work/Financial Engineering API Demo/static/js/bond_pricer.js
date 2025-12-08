(() => {
  const marketsEl = document.getElementById('market');
  const presetEl = document.getElementById('preset');
  const faceEl = document.getElementById('faceValue');
  const couponEl = document.getElementById('couponRate');
  const maturityEl = document.getElementById('maturityYears');
  const freqEl = document.getElementById('frequency');
  const marketRateEl = document.getElementById('marketRate');
  const priceEl = document.getElementById('price');
  const formErrorEl = document.getElementById('formError');

  const metricPrice = document.getElementById('metricPrice');
  const metricYtm = document.getElementById('metricYtm');
  const metricCurrentYield = document.getElementById('metricCurrentYield');
  const metricDuration = document.getElementById('metricDuration');
  const legendYtm = document.getElementById('legendYtm');
  const legendMarket = document.getElementById('legendMarket');
  const yieldFill = document.getElementById('yieldFill');
  const marketMarker = document.getElementById('marketMarker');
  const cashflowBody = document.querySelector('#cashflowTable tbody');

  const presetsByMarket = window.BOND_PRESETS || {};
  const markets = window.BOND_MARKETS || [];

  function showError(msg) {
    formErrorEl.textContent = msg || '';
    formErrorEl.style.display = msg ? 'block' : 'none';
  }

  function populateMarkets() {
    marketsEl.innerHTML = '';
    markets.forEach(mkt => {
      const opt = document.createElement('option');
      opt.value = mkt;
      opt.textContent = mkt;
      marketsEl.appendChild(opt);
    });
  }

  function populatePresets() {
    const market = marketsEl.value;
    const presets = presetsByMarket[market] || [];
    presetEl.innerHTML = '';
    presets.forEach((p, idx) => {
      const opt = document.createElement('option');
      opt.value = p.id;
      opt.textContent = `${p.name} (${p.coupon_rate_pct}% / ${p.years_to_maturity}y)`;
      if (idx === 0) opt.selected = true;
      presetEl.appendChild(opt);
    });
    if (presets.length > 0) {
      applyPreset(presets[0]);
    }
  }

  function applyPreset(preset) {
    if (!preset) return;
    faceEl.value = preset.face_value ?? 1000;
    couponEl.value = preset.coupon_rate_pct ?? 0;
    maturityEl.value = preset.years_to_maturity ?? 1;
    freqEl.value = preset.frequency ?? 2;
    marketRateEl.value = preset.market_rate_pct ?? '';
    priceEl.value = preset.price ?? '';
    showError('');
  }

  function getSelectedPreset() {
    const market = marketsEl.value;
    const presets = presetsByMarket[market] || [];
    const targetId = presetEl.value;
    return presets.find(p => p.id === targetId);
  }

  function clamp(num, min, max) {
    return Math.min(Math.max(num, min), max);
  }

  function updateVisual(ytm, marketRate) {
    const y = typeof ytm === 'number' ? ytm : 0;
    const m = typeof marketRate === 'number' ? marketRate : 0;
    const maxVal = Math.max(y, m, 1);
    const yPct = clamp((y / maxVal) * 100, 0, 100);
    const mPct = clamp((m / maxVal) * 100, 0, 100);
    yieldFill.style.width = `${yPct}%`;
    marketMarker.style.left = `${mPct}%`;
    legendYtm.textContent = `YTM: ${y ? y.toFixed(2) + '%' : '–'}`;
    legendMarket.textContent = `Market: ${m ? m.toFixed(2) + '%' : '–'}`;
  }

  function renderCashflows(cashflows) {
    cashflowBody.innerHTML = '';
    if (!cashflows || cashflows.length === 0) {
      const row = document.createElement('tr');
      const td = document.createElement('td');
      td.colSpan = 4;
      td.textContent = 'No cashflows available';
      td.style.textAlign = 'center';
      td.style.color = '#a0a8b8';
      row.appendChild(td);
      cashflowBody.appendChild(row);
      return;
    }
    cashflows.forEach(cf => {
      const row = document.createElement('tr');
      const cells = [
        cf.period,
        (cf.time_years ?? 0).toFixed(2),
        (cf.cashflow ?? 0).toFixed(2),
        cf.pv !== undefined ? cf.pv.toFixed(2) : '–'
      ];
      cells.forEach(val => {
        const td = document.createElement('td');
        td.textContent = val;
        row.appendChild(td);
      });
      cashflowBody.appendChild(row);
    });
  }

  function setMetrics(data) {
    const { price, ytm_pct, current_yield_pct, duration_years, modified_duration_years, price_from_market } = data;
    metricPrice.textContent = price !== null && price !== undefined ? `$${price.toFixed(2)}` : '–';
    const ytmText = ytm_pct !== null && ytm_pct !== undefined ? `${ytm_pct.toFixed(2)}%` : '–';
    const ytmExtra = price_from_market !== null && price_from_market !== undefined && price_from_market !== price
      ? ` (price from mkt: $${price_from_market.toFixed(2)})`
      : '';
    metricYtm.textContent = ytmText + ytmExtra;
    metricCurrentYield.textContent = current_yield_pct !== null && current_yield_pct !== undefined ? `${current_yield_pct.toFixed(2)}%` : '–';
    const durationText = duration_years !== null && duration_years !== undefined ? `${duration_years.toFixed(2)}` : '–';
    const modText = modified_duration_years !== null && modified_duration_years !== undefined ? ` (mod: ${modified_duration_years.toFixed(2)})` : '';
    metricDuration.textContent = durationText + modText;
    updateVisual(ytm_pct, data.inputs?.market_rate_pct);
    renderCashflows(data.cashflows);
  }

  function collectInput() {
    const face = parseFloat(faceEl.value);
    const coupon = parseFloat(couponEl.value);
    const maturity = parseFloat(maturityEl.value);
    const freq = parseInt(freqEl.value, 10);
    const marketRateRaw = marketRateEl.value.trim();
    const priceRaw = priceEl.value.trim();

    if (isNaN(face) || face <= 0) return { error: 'Face value must be greater than 0.' };
    if (isNaN(coupon) || coupon < 0) return { error: 'Coupon rate cannot be negative.' };
    if (isNaN(maturity) || maturity <= 0) return { error: 'Years to maturity must be greater than 0.' };
    if (![1,2,4].includes(freq)) return { error: 'Frequency must be 1, 2, or 4.' };

    const payload = {
      face_value: face,
      coupon_rate_pct: coupon,
      years_to_maturity: maturity,
      frequency: freq,
      market_rate_pct: marketRateRaw === '' ? null : parseFloat(marketRateRaw),
      price: priceRaw === '' ? null : parseFloat(priceRaw),
      market: marketsEl.value,
    };

    if (payload.market_rate_pct === null && payload.price === null) {
      return { error: 'Provide a market yield or a price to solve for YTM.' };
    }
    if (payload.price !== null && payload.price <= 0) return { error: 'Price must be positive when provided.' };

    return { payload };
  }

  async function priceBond() {
    showError('');
    const { payload, error } = collectInput();
    if (error) {
      showError(error);
      return;
    }

    try {
      const resp = await fetch('/api/bond/price', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (!resp.ok) {
        const msg = await resp.json().catch(() => ({}));
        throw new Error(msg.detail || 'Failed to price bond');
      }
      const data = await resp.json();
      setMetrics(data);
    } catch (err) {
      console.error(err);
      showError(err.message || 'Pricing failed');
    }
  }

  function resetForm() {
    const preset = getSelectedPreset();
    applyPreset(preset);
    metricPrice.textContent = '–';
    metricYtm.textContent = '–';
    metricCurrentYield.textContent = '–';
    metricDuration.textContent = '–';
    updateVisual(null, null);
    renderCashflows([]);
    showError('');
  }

  function init() {
    populateMarkets();
    populatePresets();

    marketsEl.addEventListener('change', populatePresets);
    presetEl.addEventListener('change', () => applyPreset(getSelectedPreset()));
    document.getElementById('priceBondBtn').addEventListener('click', priceBond);
    document.getElementById('resetBtn').addEventListener('click', resetForm);
  }

  document.addEventListener('DOMContentLoaded', init);
})();
