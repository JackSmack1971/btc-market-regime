# Current State Assessment - Bitcoin Market Regime Analysis

## 1. System Identity
- **Core Purpose**: Multi-tier market intelligence engine for determining Bitcoin's cyclical regime using on-chain and derivative metrics.
- **Tech Stack**: Python 3.13, Pandas, Requests, Structlog, Tenacity, PyYAML.
- **Architecture Style**: Factory Pattern fetchers with Graduated Fallback Protocol and Circuit Breakers.

## 2. The Golden Path
- **Entry Point**: `main.py` (Orchestrates fetching & reporting)
- **Key Abstractions**:
  - `BaseFetcher`: Multi-tier fallback logic (Primary -> Backup -> Neutral).
  - `RegimeAnalyzer`: Weighted scoring engine with confidence adjustment.
  - `SafeNetworkClient`: Defensive networking wrapper.

## 3. Defcon Status: **STABLE**
- **Critical Risks**: High dependency on external free-tier APIs (CoinGecko, Blockchain.info).
- **Input Hygiene**: Strict JSON schema validation per endpoint; zero-division and empty-data protection in all fetchers.
- **Dependency Health**: Up-to-date; minimal external dependencies (5 main packages).

## 4. Structural Decay
- **Complexity Hotspots**: `fetchers.py` (238 lines) - contains all 8 fetcher implementations; Consider splitting into a `fetchers/` module as logic grows.
- **Abandoned Zones**: None.
- **Placeholders**:
  - `fetchers.py:L49`: `your-api-key` for Alchemy (BTC RPC).
  - `sources.yaml:L9`: Placeholder URL for CryptoQuant Primary.

## 5. Confidence Score: **0.90**
- **Coverage Estimation**: 
  - **Contract/Integration**: 100% (11/11 endpoints verified via `api_contract_test.py`).
  - **Unit**: ~60% (Scoring logic well-covered; individual fetcher edge cases primarily handled by contract tests).
- **Missing Links**: Automated unit tests for simulated circuit-breaker recovery (verified manually).

## 6. Agent Directives
- **Do Not Touch**: `SafeNetworkClient.get` (sensitive rate-limiting and UA settings).
- **Refactor Priority**:
  1. Split `fetchers.py` into individual classes in `src/fetchers/`.
  2. Implement local CSV/Parquet caching to reduce API hits.
