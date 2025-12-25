# Logic Explainability Engine

## Overview
The Logic Explainability Engine translates quantitative metrics into human-readable narratives. This increases transparency for end-users, especially when complex aggregations (like Regime Scoring) are used.

## Architecture
The engine is implemented in `src/analyzer.py` via the `get_metric_narrative` helper function and integrated into the `calculate_regime` aggregation logic.

### Core Logic
1. **Metric Mapping**: Translates raw metric IDs (`fear_greed_index`) into human-readable labels ("Fear & Greed Index").
2. **Sentiment Analysis**: Maps scores to qualitative descriptors (Bullish/Bearish).
3. **Intensity Calculation**: Determines the strength of the signal (Extreme/Strong/Moderate).
4. **Context Injection**: Provides indicator-specific context (e.g., RSI overbought/oversold levels).

## Implementation Example
```python
def get_metric_narrative(metric_name: str, score: float, value: float) -> str:
    # ... logic to generate string ...
    return f"{label} shows {context} ({sentiment})."
```

## System Standardization
The engine relies on a standardized `score` key across all modules (analyzer, forecaster, optimizer, charts). Legacy `total_score` keys have been deprecated to ensure consistent data contracts.

## UI Integration
The narratives are displayed as an "Intelligence Briefing" in the dashboard, providing bulleted insights directly from the top market drivers.
