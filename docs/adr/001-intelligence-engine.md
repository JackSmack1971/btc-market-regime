# ADR 001: Intelligence Engine Architecture

## Status
**Accepted** (2025-12-25)

## Context
The current BTC Market Regime system operates as a modular monolith. While functional, it faces three scaling friction points:
1. **Latency**: Synchronous fetching blocks the UI for 5-8 seconds during refreshes.
2. **Persistence**: Disk-based pickle caching (`.pkl`) is prone to corruption and lacks queryability.
3. **Concurrency**: Future Phase 2.4/2.5 requirements (WebSockets, high-freq data) will overwhelm the current execution model.

We need a long-term architectural path that balances professional performance with the maintenance reality of a solo developer (Solo Trader Persona).

## Decision
We will adopt an **Async-First Modular Monolith** architecture with **SQLite Persistence**.

### Key Components:
- **Async Execution**: Refactor all fetchers to use `asyncio` and `aiohttp` for parallel, non-blocking data retrieval.
- **SQLite Storage**: Replace pickle files with a lightweight SQLite database for robust, relational storage of historical scores and price data.
- **Background Worker Pattern**: Use a dedicated background thread/loop within the process to handle long-running WebSocket streams or recurring fetches, decoupled from the Streamlit UI loop.

## Alternatives Considered

### 1. Local Micro-Services (FastAPI + Redis)
- **Pros**: Engine can run 24/7 independently of the UI.
- **Cons**: High operational overhead (managing multiple processes, ports, and IPC). Rejected as "overkill" for initial solo-user desktop needs.

### 2. Event-Driven Agentic Mesh (NATS)
- **Pros**: Maximum flexibility and resilience.
- **Cons**: Extreme complexity and debugging difficulty. Rejected to avoid "Architectural Over-Engineering" debt.

## Consequences

### Positive
- **Performance**: UI refreshes will become near-instant (<500ms for parallel fetches).
- **Maintainability**: Low operational overhead (single process to start).
- **Data Integrity**: SQLite provides ACID compliance and easier data auditing.

### Negative
- **Refactoring Effort**: Requires converting synchronous fetch logic to `async`.
- **Complexity**: Managing an async loop alongside Streamlit requires careful initialization.

## Status
**ACCEPTED** - Target implementation phase: 3.0 (Operational Excellence).
