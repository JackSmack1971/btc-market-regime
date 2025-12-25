# API Documentation & Metric Schema
*Version 1.1 | Async-First Modular Context*

## 1. Metric Definition Matrix
| Metric | Code Key | Type | Confluence Weight |
|--------|----------|------|-------------------|
| Fear & Greed | `fear_greed_index` | Sentiment | 1.0 |
| Hash Rate | `hash_rate` | Momentum | 0.8 |
| MVRV Ratio | `mvrv_ratio` | Valuation | 0.9 |
| Funding Rate| `perpetual_funding_rates` | Derivatives | 1.0 |
| RSI (14d) | `price_data` | Oscillator | 0.6 |

## 2. Core Data Contracts

### MetricData (Raw Retrieval)
The object produced by `src/fetchers/` and consumed by the `RegimeAnalyzer`.
- `metric_name`: (str) Unique identifier.
- `value`: (float) Raw numeric signal.
- `timestamp`: (datetime) Retrieval UTC mark.
- `source`: (str) "primary" or "backup".
- `is_fallback`: (bool) True if Tier 2 retrieval was triggered.

### ScoredMetric (Processed)
- `metric_name`: (str) Unique identifier.
- `score`: (float) [-1.0, 1.0] intensity.
- `confidence`: (str) HIGH | MEDIUM | LOW.
- `is_fallback`: (bool) Source status.

## 3. High-Performance Retrieval (`SafeNetworkClient`)
Integrated via `src/fetchers/base.py`.
- **Latency Control**: 0.5s mandatory sleep between serial requests (Async).
- **Timeout**: 5s global hard limit per request.
- **Provider Parity**: All fetchers utilize a shared `aiohttp` session for connection pooling efficiency.

## 4. Aggregate Response Schema (`main.py --json`)
The standardized output for external consumption.
```json
{
  "engine_version": "1.0.0",
  "timestamp": "2025-12-25T15:43:54Z",
  "score": 1.6,
  "label": "SIDEWAYS/TRANSITIONAL",
  "confidence": "HIGH",
  "breakdown": [
    {
      "metric_name": "fear_greed_index",
      "score": -1.0,
      "raw_value": 23.0,
      "confidence": "HIGH",
      "is_fallback": false
    }
  ]
}
```

## 5. Logical Schemas
Internal JSON structure for SQLite caching:
```json
{
  "metric_name": "fear_greed_index",
  "value": 45.0,
  "timestamp": "2025-12-25T15:05:00Z",
  "source": "primary",
  "is_fallback": false
}
```
