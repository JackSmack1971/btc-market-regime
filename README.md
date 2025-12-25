# Bitcoin Market Regime Analysis Tool

A professional-grade market intelligence engine designed to determine the current Bitcoin market regime (Bullish, Bearish, or Sideways) by aggregating multiple on-chain and derivative metrics.

## 🚀 Vision
Built for resilience and accuracy. This tool uses a **Multi-Tier Fallback Protocol** to ensure that even during API outages or regional restrictions, the analytical pipeline remains functional and unbiased.

## 🛠 Features
- **Resilient Data Fetching**: Tiered retrieval (Primary -> Backup -> Neutral) with automated circuit breakers.
- **Quantitative Scoring**: Weighted aggregation of 8 specialized indicators:
  - Fear & Greed Index
  - Network Hash Rate (Momentum)
  - Exchange Net Flows
  - Active Addresses
  - Perpetual Funding Rates
  - Open Interest (Aggregate BTC)
  - MVRV Ratio
  - RSI (14-day)
- **Hardened Networking**: Defensive UA headers, consistent timeouts, and rate-limiting.
- **Forensic QA**: Automated schema validation to detect and report API drift.

## 📥 Installation

### Prerequisites
- Python 3.10+
- Pip

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/btc-market-regime.git
   cd btc-market-regime
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Keys (Optional)**:
   Edit `config/sources.yaml` to add your CryptoQuant or Alchemy keys if available.

## ⚡ Usage

Run the main analysis engine to see the current market regime:
```bash
python main.py
```

### Advanced Options
- **JSON Output**: `python main.py --json` (Ideal for piping to scripts or monitoring tools)
- **Historical Backtest**: `python main.py --days 30 --export results.csv` (Analyze and export time-series data)
- **MTF Confluence**: `python main.py --mtf` (Fractal analysis: Daily, Weekly, Monthly alignment)
- **Metric Guide**: `python main.py --help-metrics` (Explains the logic behind each indicator)
- **Custom Config**: `python main.py --sources my_sources.yaml --thresholds my_thresholds.yaml`

### Logic/Log Separation
The engine follows the **Admin/Quant Persona** best practices:
- **STDOUT**: Pure data (ASCII tables or JSON).
- **STDERR**: Structured logging (Execution traces, errors).

Example pipe to file:
```bash
python main.py --json > regime.json 2> logs.txt
```

## 🧪 Testing
Run the forensic API contract audit to certify zero drift:
```bash
python tests/api_contract_test.py
```

## 🏗 Architecture
- `src/fetchers.py`: The data retrieval layer with fallback logic.
- `src/analyzer.py`: The scoring engine and aggregation logic.
- `config/thresholds.yaml`: Centralized configuration for bullish/bearish boundaries.
- `config/sources.yaml`: API endpoint management.

## ⚖️ License
MIT License. See `LICENSE` for details.
