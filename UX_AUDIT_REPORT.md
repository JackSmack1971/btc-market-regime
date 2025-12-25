# UX Audit Report: Bitcoin Market Regime Analysis

## 1. Persona Profiles & Mental Models

### 👤 The Crypto Quant (Alex)
- **Mental Model:** "I need raw, high-fidelity data to integrate into my Python workflow."
- **Expected Outcome:** Machine-readable output (JSON) and historical backfill capabilities.

### 👤 The Passive Investor (Sarah)
- **Mental Model:** "I want to know the market sentiment without being an expert in on-chain logic."
- **Expected Outcome:** High signal-to-noise ratio, clear actionable verdict, and minimal jargon.

### 👤 The Reliability Engineer (Marco)
- **Mental Model:** "I need to ensure this script runs in a headless environment with clean logs."
- **Expected Outcome:** Separation of data (STDOUT) and logs (STDERR), easy configuration, and resilient error recovery.

---

## 2. Friction Analysis (Implementation vs. Mental Model)

| Friction Point | Persona Affected | Conflict Description |
|----------------|-------------------|----------------------|
| **Log Interleaving** | Admin (Marco) | Structured JSON logs are currently printed alongside ASCII tables on STDOUT, making it difficult to pipe/parse data. |
| **Jargon Wall** | Novice (Sarah) | "MVRV", "Hash Rate", and "Open Interest" are shown without context. A non-technical user feels overwhelmed by the metric table. |
| **Static Output** | Quant (Alex) | The output is purely visual. There is no flag to request JSON format or specific metrics, forcing manual reading. |
| **Verdict Obscurity** | Novice (Sarah) | The "Final Regime" verdict (the most important info) is at the very bottom, appearing secondary to the large table of raw data. |

---

---

## 4. Post-Refinement Audit: Progress & Secondary Friction

### ✅ Progress (Resolved Friction)
- **Log/Logic Separation:** Marco can now pipe STDOUT to databases without parsing logic logs.
- **Visual Hierarchy:** Sarah immediately notes the "SIDEWAYS/TRANSITIONAL" verdict in yellow at the top.
- **Machine Format:** Alex has 1-click access to the full analysis via `--json`.

### ⚠️ Secondary Friction (Audit 2)
- **Temporal Blindness:** The `--json` output lacks a `timestamp` field. Alex needs to know *at what exact moment* the analysis was frozen.
- **Configuration Ghosts:** When using custom `--sources`, there is no explicit confirmation on STDOUT/STDERR about which configuration file was successfully parsed.
- **Failure Transparency:** Sarah sees "Confidence: MEDIUM" but doesn't intuitively know this is due to a primary API failure (fallback in effect).

## 5. Next-Level Polish Roadmap (Recommended)
- [ ] **Analysis Metadata:** Add `timestamp` and `engine_version` to both JSON and Table outputs.
- [ ] **Config Traceability:** Emit a "Loading config from [path]" log on STDERR at startup.
- [ ] **Resilience Indicators:** Add a `[*]` or `[FALLBACK]` marker in the ASCII table next to metrics where the primary source failed.

---
**Final Verdict (Audit 2):** The tool has transitioned from a "Developer Script" to a **"Professional CLI Utility."** It is now stable, resilient, and persona-aligned.
