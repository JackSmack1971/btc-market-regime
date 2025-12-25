# UX Audit Report: BTC Market Regime Dashboard

**Audit Date**: 2025-12-25
**Scope**: Interactive Dashboard (v1.0) & MTF Confluence Engine

## 1. Persona Analysis

| Persona | Archetype | Primary Need |
| :--- | :--- | :--- |
| **Novice Nina** | Casual HODLer | "Tell me if I should panic or buy more." |
| **Quant Alex** | Active Trader | "Show me the math and the raw data sources." |
| **Macro Marco** | Cycle Investor | "Are the daily fluctuations aligned with the monthly trend?" |

## 2. Cognitive Walkthroughs

### Novice Nina
- **Mental Model**: Expects a "Green = Good", "Red = Bad" interface.
- **Friction**:
  - The term "MVRV Ratio" and "Funding Rates" in the breakdown table are opaque.
  - The "Total Score" (e.g. 4.21) lacks context—is that out of 10? Out of 100?
  - **Missing Connection**: Needs a "Why this matters" tooltip or simple explanation.

### Quant Alex
- **Mental Model**: Needs to audit the tool's reasoning.
- **Friction**:
  - The dashboard caches results, but he wants to know *exactly* when the last fetch occurred.
  - The historical chart shows the score, but not the underlying raw values (Price vs Score overlay).
  - **Feedback Loop**: He wants a way to see "Raw Logs" for the fetcher to verify backup tier usage.

### Macro Marco
- **Mental Model**: Looking for fractal alignment.
- **Friction**:
  - The "Macro Thesis" is a text box, but the individual alignments (Daily vs Weekly vs Monthly) are in separate chunks.
  - He has to scroll to see the historical chart after reading the thesis.
  - **Visual Gap**: A "Confluence Gauge" or Radar chart would communicate alignment faster than a bar chart.

## 3. Top Friction Points

1. **Jargon Barrier**: Metric names are technically accurate but cognitively heavy for non-quants.
2. **Score Ambiguity**: Magnitude of the "Total Score" is undefined visually (needs a range indicator).
3. **Data Freshness**: Cache indicators are present but secondary; Alex wants more prominent fetch timestamps.
4. **Visual Hierarchy**: The "Macro Thesis" (the most valuable output for Marco) is secondary to the KPI cards.

## 4. Proposed Improvement Tasks

- [ ] **Task 1**: Add metric descriptions (tooltips) using `st.help` or expanders.
- [ ] **Task 2**: Implement a "Score Gauge" (0-10 or -5 to +5 scale) instead of a simple metric.
- [ ] **Task 3**: Overlay BTC Price on the Historical Regime Chart for better correlations.
- [ ] **Task 4**: Add a "Technical Logs" expander for Quant Alex (showing primary vs backup success).
