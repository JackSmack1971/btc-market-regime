# API Documentation & Metric Schema

This document details the data structures and metrics utilized by the Regime Analysis Engine.

## 1. Metric Breakdown

| Metric | Source (Primary) | Type | Bullish Signal | Bearish Signal |
|--------|------------------|------|----------------|----------------|
| **Fear & Greed** | Alternative.me | Sentiment | Score > 70 | Score < 30 |
| **Hash Rate** | Blockchain.info | Momentum | > 1.1x MA30 | < 0.9x MA30 |
| **MVRV Ratio** | CoinMetrics | Valuation | < 1.0 (Undervalued) | > 3.0 (Overvalued) |
| **Funding Rate**| Binance | Derivatives | > 0.01% (Premium) | < -0.01% (Discount)|
| **RSI (14d)** | CoinGecko | Oscillator | < 30 (Oversold) | > 70 (Overbought) |

## 2. Global Data structures

### MetricData (Internal)
The raw object returned by fetchers after successful retrieval or fallback.
- `metric_name`: (str) e.g., "fear_greed_index"
- `value`: (float) Numeric metric value.
- `timestamp`: (ISO8601) Fetch time.
- `source`: (str) "primary", "backup", or "failed".

### ScoredMetric (Processed)
The object used by the analyzer for final aggregation.
- `score`: (float) Weighted impact (-1.0 to 1.0).
- `confidence`: (str) Quality tier (HIGH/MEDIUM/LOW).

## 3. Fallback Protocol (Forensic)
All API endpoints are validated against their forensic schema defined in `tests/api_contract_test.py`.

### Schema Example (CoinMetrics MVRV)
```json
{
  "data": [
    {
      "asset": "btc",
      "time": "2025-09-17T00:00:00Z",
      "CapMVRVCur": "2.18"
    }
  ]
}
```

## 4. Rate Limiting
The `SafeNetworkClient` enforces a **1-second delay** between all external requests to ensure compliance with free-tier API usage policies.
