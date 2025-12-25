# ARCHITECTURAL DECISION RECORDS (ADR)

## Stack Selection Logic (Source: Pattern #3)
| Scenario | Stack | Rationale |
| :--- | :--- | :--- |
| **MVP / Single User** | Streamlit + SQLite | Rapid iteration, low overhead. |
| **Scale / Multi-User** | React + Zustand + FastAPI | Required for interactive charts & high concurrency. |

## Domain Strategy: Crypto Forensics (Source: Pattern #5)
- **Primary Signal**: Hash Ribbons "Buy" post-capitulation.
- **Confirmation**: Triangulate with MVRV Z-Score and ETF Flows.
