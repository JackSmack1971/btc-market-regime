# Multi-Tier Fallback Fetching Pattern

## Context
Use this pattern when building data retrieval systems that must be resilient to API instability, rate limiting, or location-based blocks (e.g., Binance 451).

## Problem
Single-source data fetching creates a single point of failure. API drift or transient errors can crash an analytical pipeline or lead to biased results.

## Solution
Implement a three-tier retrieval structure:
1.  **Tier 1 (Primary)**: The highest-fidelity source with retries and exponential backoff.
2.  **Tier 2 (Backup)**: A fundamentally different source (different data provider) to use if Tier 1 is exhausted or fails circuit breaker checks.
3.  **Tier 3 (Degraded/Neutral)**: A safe fallback value (usually 0.0 or a neutral constant) that prevents the aggregate analysis from being biased by the missing data.

### Structural Skeleton (Python)
```python
class BaseFetcher(ABC):
    def fetch(self) -> Optional[MetricData]:
        # Tier 1: Primary Attempt
        if circuit_breaker.is_available("primary"):
            try:
                return self.fetch_primary()
            except Exception:
                circuit_breaker.report_failure("primary")

        # Tier 2: Backup Attempt
        try:
            return self.fetch_backup()
        except Exception:
            # Tier 3: Critical Failure Mode
            return MetricData(value=0.0, source="failed")
```

## Gotchas
- **Score Bias**: Ensure Tier 3 returns a value that is truly "neutral" for your specific scoring algorithm (e.g., 0.0 in a centered score, or the distribution mean).
- **Circuit Breakers**: Always use circuit breakers to avoid hammering a dying API and to speed up the switch to backups.
