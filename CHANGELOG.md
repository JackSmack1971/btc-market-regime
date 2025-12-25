# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-12-25

### Added
- **Core Engine**: Initial implementation of the Regime Analysis Engine.
- **Resilience**: Multi-Tier Fallback Protocol (Primary -> Backup -> Neutral).
- **Networking**: `SafeNetworkClient` with UA injection, timeouts, and rate limiting.
- **Indicators**: Support for 8 specialized metrics (Fear & Greed, MVRV, RSI, etc.).
- **Forensic QA**: API Contract validation suite with deep schema checking.
- **Formal Verification**: Clover Trifecta certification (Code vs Docstring vs Spec).
- **Knowledge Base**: Architectural recipes for fallback fetching and networking.
- **Documentation**: Google-style docstrings, README, and API schemas.
- **UX Refinement**: Logic/Log separation (STDERR routing), JSON output support, and interactive metric guides.
- **Dependency Hardening**: Pinned all core dependencies to strict stable versions for 100% build reproducibility.
- **Security Audit**: Completed forensic vulnerability scan with zero high-risk results in the project scope.
- **Resilience Transparency**: Added temporal metadata and visual indicators (`[*]`) for fallback data sources.
- **Historical Backtesting (Phase 21)**: Added `--days` and `--export` support for time-series regime analysis over N days.
- **MTF Confluence Engine (Phase 22)**: Added `--mtf` flag for fractal (Daily/Weekly/Monthly) trend alignment and "Macro Thesis" generation.

### Changed
- **Indicator Logic**: Refactored RSI and MVRV calculation for zero-division protection.
- **Fallback Targets**: Updated backup sources for Hash Rate (mempool.space) and Active Addresses (Blockchair).
- **Reporting**: ASCII-table output with bold caps and structured log events.

### Fixed
- **API Drift**: Resolved CoinMetrics MVRV schema mismatch detected during forensic probes.
- **Resilience**: Fixed Binance 451 location restriction handling via graceful fallback to CoinGecko.
- **Accuracy**: Fixed CoinGecko Perpetual Funding Rate targeting logic.

## [0.1.0] - 2025-12-25
- Initial Project Skeleton.
- Basic API fetchers and analyzer.
