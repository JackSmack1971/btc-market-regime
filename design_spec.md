# Bitcoin Market Regime Analysis - Design Specification
*Version 1.0 | Generated 2025-12-25*

---

## 1. Data Sources & Fallback Matrix

| Metric | Primary Source | Backup Source | Failure Action | Weight |
|--------|---------------|---------------|----------------|--------|
| Fear & Greed Index | Alternative.me API | Manual calc from volatility | Return score=0, confidence=LOW | 1.0 |
| Bitcoin Hash Rate | Blockchain.com | BTC.com (derive from difficulty) | Return score=0, confidence=LOW | 0.8 |
| Exchange Net Flows | CryptoQuant Community API | Manual On-Chain Calculation | Return score=0, confidence=LOW | 0.9 |
| Active Addresses | Blockchain.com | Messari API | Return score=0, confidence=LOW | 0.7 |
| Perpetual Funding Rates | Binance API | CoinGecko | Return score=0, confidence=LOW | 1.0 |
| Open Interest | CoinGecko | Coinglass API | Return score=0, confidence=LOW | 0.8 |
| MVRV Ratio | CoinMetrics Community API | Blockchain.com | Return score=0, confidence=LOW | 0.9 |
| RSI | Manual Calculation (CoinGecko) | None | Return score=0, confidence=LOW | 0.6 |

**Source Independence Verification:**
- ✓ No two primary sources share the same API provider
- ✓ Backup sources use fundamentally different data (not just alternate endpoints)

---

## 2. Failure Protocol Specification

### 2.1 Error Classification & Actions
```python
# Error Taxonomy
class ErrorType:
    NETWORK_ERROR = "Transient connectivity issue"
    TIMEOUT_ERROR = "Request exceeded time limit"
    PARSE_ERROR = "Invalid JSON/data format"
    RATE_LIMIT_ERROR = "API quota exceeded"
    AUTH_ERROR = "Invalid or expired API key"
```

### 2.2 Graduated Fallback Protocol

**Tier 1: Optimistic Primary Attempt**
```python
@retry(
    max_attempts=3,
    backoff=ExponentialBackoff(base=2, max_delay=16),
    retry_on=[NetworkError, TimeoutError]
)
def fetch_primary_source(metric_name: str) -> MetricData:
    """
    Attempts: 3 (delays: 2s, 4s, 8s)
    Timeout: 10s per request
    """
    try:
        response = requests.get(PRIMARY_URL, timeout=10)
        return parse_response(response)
    except (NetworkError, TimeoutError) as e:
        logger.warning(f"Primary failed for {metric_name}: {e}")
        raise  # Trigger retry
```

**Tier 2: Coordinated Backup Attempt**
```python
def fetch_with_fallback(metric_name: str) -> MetricData:
    try:
        return fetch_primary_source(metric_name)
    except MaxRetriesExceeded:
        logger.error(f"Primary source exhausted for {metric_name}")
        
        # Open circuit breaker (5min cooldown)
        circuit_breaker.open(f"primary_{metric_name}", duration=300)
        
        # Attempt backup
        try:
            return fetch_backup_source(metric_name)
        except Exception as e:
            logger.critical(f"Backup also failed for {metric_name}: {e}")
            # Fall through to Tier 3
```

**Tier 3: Degraded Mode**
```python
def fetch_with_degradation(metric_name: str) -> ScoredMetric:
    try:
        data = fetch_with_fallback(metric_name)
        return calculate_score(data, confidence="HIGH")
    except AllSourcesUnavailable:
        logger.error(
            f"All sources unavailable for {metric_name}",
            extra={"metric": metric_name, "timestamp": now()}
        )
        return ScoredMetric(
            score=0,  # Neutral (no bias)
            confidence="LOW",
            reason="data_unavailable",
            metric_name=metric_name
        )
```

### 2.3 Circuit Breaker Configuration
```python
CIRCUIT_BREAKER_CONFIG = {
    "failure_threshold": 3,      # Open after 3 consecutive failures
    "recovery_timeout": 300,     # 5min cooldown before retry
    "half_open_max_calls": 1     # Test with 1 call when recovering
}
```

### 2.4 Logging Standards
```python
import structlog

logger = structlog.get_logger()

# Format: JSON with required fields
{
    "timestamp": "2024-01-15T14:30:00Z",
    "level": "ERROR",
    "metric": "fear_greed_index",
    "source": "alternative.me",
    "error_type": "NetworkError",
    "retry_count": 3,
    "circuit_state": "OPEN"
}
```

---

## 3. Scoring Algorithm

### 3.1 Individual Metric Scoring
```python
def score_metric(value: float, thresholds: dict, weight: float) -> float:
    """
    Returns: -1 (bearish), 0 (neutral), +1 (bullish)
    Weighted by metric.weight
    """
    if value > thresholds['bull']:
        return 1.0 * weight
    elif value < thresholds['bear']:
        return -1.0 * weight
    else:
        return 0.0
```

### 3.2 Aggregate Regime Calculation
```python
def calculate_regime(metric_scores: List[ScoredMetric]) -> Regime:
    """
    Aggregates weighted scores from all metrics.
    
    Regime Thresholds:
    - BULL: total_score > 3.0
    - BEAR: total_score < -3.0
    - NEUTRAL: -3.0 <= total_score <= 3.0
    
    Confidence Adjustment:
    - If >30% of metrics have confidence=LOW: Reduce regime confidence
    """
    total_score = sum(m.score for m in metric_scores)
    low_confidence_pct = sum(1 for m in metric_scores if m.confidence == "LOW") / len(metric_scores)
    
    regime_confidence = "HIGH" if low_confidence_pct < 0.3 else "MEDIUM"
    
    if total_score > 3.0:
        return Regime(label="BULL", score=total_score, confidence=regime_confidence)
    elif total_score < -3.0:
        return Regime(label="BEAR", score=total_score, confidence=regime_confidence)
    else:
        return Regime(label="NEUTRAL", score=total_score, confidence=regime_confidence)
```

### 3.3 Threshold Examples
| Metric | Bull Threshold | Bear Threshold | Weight |
|--------|---------------|----------------|--------|
| Fear & Greed Index | > 70 | < 30 | 1.0 |
| Bitcoin Hash Rate | > 30-day MA + 10% | < 30-day MA - 10% | 0.8 |
| Exchange Net Flows | < 0 | > 0 | 0.9 |
| Active Addresses | > 30-day MA + 5% | < 30-day MA - 5% | 0.7 |
| Perpetual Funding Rates | > 0.01% | < -0.01% | 1.0 |
| Open Interest | Rising > 5% MoM | Declining > 5% MoM | 0.8 |
| MVRV Ratio | < 1 | > 3 | 0.9 |
| RSI | < 30 | > 70 | 0.6 |

---

## 4. Project File Structure
```
bitcoin-regime-analyzer/
├── src/
│   ├── fetchers.py          # API clients with fallback logic
│   │   ├── AlternativeMeFetcher
│   │   ├── BlockchainComFetcher
│   │   └── [8+ source-specific classes]
│   │
│   ├── analyzer.py          # Scoring & regime calculation
│   │   ├── score_metric()
│   │   ├── calculate_regime()
│   │   └── RegimeAnalyzer class
│   │
│   ├── utils.py             # Shared utilities
│   │   ├── retry decorators
│   │   ├── circuit_breaker.py
│   │   └── structured_logger.py
│   │
│   └── models.py            # Data classes
│       ├── MetricData
│       ├── ScoredMetric
│       └── Regime
│
├── tests/
│   ├── test_fetchers.py     # Unit tests for each fetcher
│   ├── test_analyzer.py     # Scoring logic tests
│   └── test_fallbacks.py    # Failure simulation tests
│
├── config/
│   ├── sources.yaml         # API endpoints & credentials
│   └── thresholds.yaml      # Metric thresholds
│
├── main.py                  # CLI entry point
├── requirements.txt         # Dependencies (requests, structlog, tenacity)
├── README.md                # Usage guide
└── design_spec.md           # THIS FILE
```
