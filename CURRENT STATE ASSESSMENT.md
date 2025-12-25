# CURRENT STATE ASSESSMENT - [2025-12-25]

## 1. System Identity
- **Core Purpose**: High-fidelity BTC Market Regime Intelligence & Forecasting.
- **Tech Stack**: Python 3.13, Streamlit (UI), aiohttp (Async), SQLite3 (Persistence), Scikit-learn (ML), Optuna (Optimization).
- **Architecture Style**: **Async-First Modular Monolith**.

## 2. The Golden Path
- **Entry Point**: `app.py` (Dashboard) / `main.py` (CLI Orchestrator).
- **Key Abstractions**: 
    - `FetcherFactory`: Dynamic modular retrieval.
    - `BaseFetcher`: Graduated Fallback Protocol (Primary -> Backup -> Failed).
    - `RegimeAnalyzer`: Strategy-based aggregate scoring & MTF confluence.
    - `db_manager.py`: ACID-compliant SQLite caching layer.

## 3. Defcon Status
- **Critical Risks**: ⚠️ Upstream API rate limits (Mitigated via Circuit Breaker). ⚠️ Latency spikes from free-tier providers.
- **Input Hygiene**: COMPLIANT. `SafeNetworkClient` (Async) handles retries/timeouts; no hardcoded secrets found.
- **Dependency Health**: HEALTHY. Version 3.13 parity confirmed; minimal transitive footprint.

## 4. Structural Decay
- **Complexity Hotspots**:
    - `src/analyzer.py` (232 lines): Orchestrates all scoring strategy routing.
    - `main.py` (232 lines): Handles diverse CLI workflows (MTF, Historical, Snapshot).
- **Abandoned Zones**: NONE. Legacy pickle caching (`.cache/`) is deprecated but accessible for migration reference.

## 5. Confidence Score: [0.95]
- **Coverage Estimation**: 55-65% (Unit tests for Fetchers, Intelligence, and Analysis present).
- **Missing Links**: Full end-to-end integration suite for the Sidebar HUD alerting logic.

## 6. Agent Directives
- **"Do Not Touch" List**: 
    - `src/persistence/db_manager.py`: Core relational integrity.
    - `src/fetchers/base.py`: Core async retrieval logic.
- **Refactor Priority**:
    - [MEDIUM] Implement Strategy Pattern for specific indicator math in `analyzer.py`.
    - [LOW] Expand forecasting horizons beyond 12-hour linear models.
