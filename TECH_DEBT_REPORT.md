# Technical Debt Report - Bitcoin Market Regime Analysis

## 1. Complexity Scan (Refactoring Candidates)

### 🔴 High Priority: `src/fetchers.py`
- **Metric**: 297 lines (Approaching the 300-line threshold).
- **Issue**: **Class Density**. This file contains 8 indicator fetcher implementations plus a factory and a safe network client.
- **Volatility**: High. This file is the primary target for any new data source additions.
- **Recommendation**: Split `fetchers.py` into a `src/fetchers/` directory with individual files per indicator (e.g., `src/fetchers/fear_greed.py`, `src/fetchers/on_chain.py`).

### 🟡 Medium Priority: `src/analyzer.py`
- **Metric**: `score_metric` function depth.
- **Issue**: **Indicator Routing Logic**. The large `if/elif` block used to route scores to different logic (Momentum vs Absolute vs Mean Reversion) is functional but will become brittle as indicators increase.
- **Recommendation**: Implement a **Strategy Pattern** for indicator scoring logic to decouple the `RegimeAnalyzer` from specific indicator math.

## 2. Comment Audit (Debt Markers)
- **Grep Results**: `TODO`: 0, `FIXME`: 0, `HACK`: 0, `XXX`: 0.
- **Verdict**: The codebase is exceptionally clean of "lazy debt". All logic is implemented to the specified Senior Standards.

## 3. Dependency Rot Check
- **Status**: **HEALTHY**
- **Audit Results**: 
  - `requests`: Modern (>=2.31.0)
  - `pandas`: Modern (>=2.1.0)
  - `tenacity`: Modern (>=8.2.3)
- **Action**: No immediate updates required.

## 4. Prioritized Action Plan

| Rank | Item | Category | Effort | Impact |
|------|------|----------|--------|--------|
| 1 | Modularize Fetchers | Architecture | Low | High (Maintainability) |
| 2 | Strategy Scorer | Architecture | Medium| Medium (Extensibility) |
| 3 | Caching Layer | Performance | Medium| High (Resilience) |

---
**Verdict**: Total Debt is **LOW**. The architecture is stable but needs modularization to support future scaling.
