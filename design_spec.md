# Bitcoin Market Regime Analysis - Design Specification
*Version 1.1 | Updated 2025-12-25 (Async Intelligence Evolution)*

---

## 1. Data Architecture & Retrieval Matrix

| Metric | Primary Source | Backup Source | Failure Action | Weight |
|--------|---------------|---------------|----------------|--------|
| Fear & Greed Index | Alternative.me API | Manual calc from volatility | Return score=0, confidence=LOW | 1.0 |
| Bitcoin Hash Rate | Blockchain.com | mempool.space | Return score=0, confidence=LOW | 0.8 |
| Exchange Net Flows | CryptoQuant Community API | Manual On-Chain Calculation | Return score=0, confidence=LOW | 0.9 |
| Active Addresses | Blockchain.com | Blockchair API | Return score=0, confidence=LOW | 0.7 |
| Perpetual Funding Rates | Binance API | CoinGecko | Return score=0, confidence=LOW | 1.0 |
| Open Interest | CoinGecko | Binance API | Return score=0, confidence=LOW | 0.8 |
| MVRV Ratio | CoinMetrics Community API | Blockchain.com | Return score=0, confidence=LOW | 0.9 |
| RSI | Manual Calculation (CoinGecko) | None | Return score=0, confidence=LOW | 0.6 |

---

## 2. Asynchronous Retrieval & Failure Protocol

### 2.1 Async Network Client
The system utilizes `aiohttp` for non-blocking parallel retrieval.
```python
class SafeNetworkClient:
    USER_AGENT = "BitcoinRegimeAnalyzer/1.1"
    TIMEOUT = 5 

    @staticmethod
    async def get(session: aiohttp.ClientSession, url: str) -> Any:
        async with session.get(url, timeout=SafeNetworkClient.TIMEOUT) as response:
            response.raise_for_status()
            await asyncio.sleep(0.5) # Rate limiting
            return await response.json()
```

### 2.2 Graduated Fallback Protocol (Async)
All fetchers inherit from `BaseFetcher` which implements parallel-safe retrieval.

**Optimistic Performance**:
```python
async def fetch(self, session: aiohttp.ClientSession) -> MetricData:
    cache_data = cache.get(f"{self.metric_name}_latest")
    if cache_data: return cache_data

    try:
        data = await SafeNetworkClient.get(session, self.primary_url)
        value = self.parse_primary(data)
        health_tracker.log_attempt(self.metric_name, "primary", True)
        return MetricData(value=value, source="primary")
    except Exception:
        # Tier 2: Backup Attempt
        value = await self.get_backup(session)
        return MetricData(value=value, source="backup")
```

### 2.3 Persistence Specification (SQLite)
Legacy `.pkl` files are deprecated in favor of an ACID-compliant SQLite layer.
- **Table**: `cache` (key TEXT PRIMARY KEY, value BLOB, timestamp DATETIME)
- **Logic**: Objects are serialized via `pickle` and stored as BLOBs to preserve type fidelity for `MetricData` class instances.

---

## 3. Intelligence Suite

### 3.1 ML Regime Forecasting
Experimental 12-hour projections based on historical regime scores.
- **Model**: Linear Regression / Polynomial features of recent total scores.
- **Output**: `Projected Score` and `Sentiment Trend`.

### 3.2 Backtest Optimizer
Bayesian optimization (Optuna) for indicator weight adjustment.
- **Objective**: Maximize "Regime Predictive Accuracy" against historical price action.
- **Parameters**: `fear_greed_weight`, `mvrv_weight`, etc.

---

## 4. Project File Structure (Modular Monolith)
```
bitcoin-regime-analyzer/
├── src/
│   ├── fetchers/            # Async fetcher package
│   │   ├── base.py          # Abstract BaseFetcher
│   │   ├── sentiment.py     # FearGreedFetcher
│   │   └── [Specialized...]
│   │
│   ├── persistence/         # SQLite persistence logic
│   │   └── db_manager.py    # CRUD for cache table
│   │
│   ├── intelligence/        # ML & Optimizer suite
│   │   ├── forecaster.py
│   │   └── optimizer.py
│   │
│   ├── ui/                  # Dashboard components
│   │   ├── dashboard.py     # Main layout logic
│   │   └── charts.py        # Plotly implementations
│   │
│   ├── analyzer.py          # Scoring engine
│   ├── models.py            # Data contracts
│   └── utils/               # Health, Alerts, Networking
│
├── config/                  # Thresholds & Sources
├── main.py                  # ASYNC CLI entry point
└── design_spec.md           # THIS FILE
```
