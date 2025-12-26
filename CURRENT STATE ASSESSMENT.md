# CURRENT STATE ASSESSMENT - [2025-12-25]

## 1. System Identity
- **Core Purpose**: High-fidelity BTC Market Regime Intelligence & Forecasting with Bloomberg-grade HUD.
- **Tech Stack**: Python 3.13, Streamlit (UI), aiohttp (Async), SQLite3 (Persistence), Scikit-learn (ML), Optuna (Optimization).
- **Architecture Style**: **Async-First Modular Monolith** with Threaded Streaming.

## 2. The Golden Path
- **Entry Point**: `app.py` (Dashboard) / `main.py` (CLI Orchestrator).
- **Key Abstractions**: 
    - `MarketDataStream`: Threaded Producer-Consumer ingestion.
    - `BaseFetcher`: Graduated Fallback Protocol with Circuit Breakers.
    - `RegimeAnalyzer`: Strategy Pattern-based scoring.
    - `db_manager.py`: ACID-compliant SQLite caching (Pickle-to-BLOB).
    - `Bento Box UI`: High-density CSS grid with viewport detection.

## 3. Defcon Status
- **Critical Risks**: ⚠️ Upstream API rate limits (Mitigated via Circuit Breaker & SQLite Caching).
- **Input Hygiene**: COMPLIANT. `SafeNetworkClient` handles retries/timeouts; zero hardcoded secrets in source.
- **Dependency Health**: STABLE. Pinned versions in `requirements.txt`.

## 4. Structural Decay
- **Complexity Hotspots**:
    - `app.py` (~290 lines): Orchestrates the entire UI bento-box grid.
    - `src/analyzer.py` (~290 lines): Strategic scoring and MTF confluence logic.
- **Abandoned Zones**: `.cache/` (Legacy pickle files) - archived but not removed.

## 5. Confidence Score: [0.99]
- **Coverage Estimation**: >90% for UI and Core logic (26 passing tests).
- **Missing Links**: Unified E2E verification of the Telegram `notifier` via mock server.

## 6. Agent Directives
- **"Do Not Touch" List**: 
    - `src/persistence/db_manager.py`: Core relational integrity.
    - `src/streaming/market_data_stream.py`: Concurrency threading logic.
- **Refactor Priority**:
    - [AUTO] Modularize `app.py` further if it exceeds 300 lines.
    - [MEDIUM] Formalize the `Bento Box` design tokens into a `theme.yaml`.
