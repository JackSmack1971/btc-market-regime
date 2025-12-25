import yaml
import sys
import pandas as pd
import json
import argparse
import asyncio
import aiohttp
from typing import List, Dict, Any
from datetime import datetime
from src.fetchers import FetcherFactory
from src.analyzer import RegimeAnalyzer, calculate_regime, analyze_history
from src.models import ScoredMetric
from src.utils import logger, RED, RESET

GREEN = "\033[92m"
YELLOW = "\033[93m"
BOLD = "\033[1m"

METRIC_HINTS = {
    "fear_greed_index": "Sentiment: High (>70) is Bullish (Extreme Greed), Low (<30) is Bearish (Fear).",
    "hash_rate": "Network Health: Momentum > 1.0 indicates miners are increasing capacity (Bullish).",
    "mvrv_ratio": "Valuation: Low (<1.0) is Undervalued/Bullish, High (>3.0) is Overvalued/Bearish.",
    "perpetual_funding_rates": "Derivatives: Positive rates mean Longs pay Shorts (Bullish premium).",
    "rsi": "Oscillator: <30 is Oversold (Bullish), >70 is Overbought (Bearish).",
    "exchange_net_flows": "Liquidity: Positive means BTC moving TO exchanges (Bearish selling pressure).",
    "active_addresses": "Adoption: Increasing unique addresses indicates growing demand.",
    "open_interest": "Leverage: High OI indicates heavy speculation/potential volatility."
}

class MarketRegimeCLI:
    def __init__(self, sources_path: str, thresholds_path: str):
        logger.info("Initializing engine (Async CLI)", sources=sources_path, thresholds=thresholds_path)
        with open(sources_path, 'r') as f:
            self.sources_config = yaml.safe_load(f)['sources']
        self.analyzer = RegimeAnalyzer(thresholds_path)

    async def run(self, args):
        """Executes the analysis workflow based on arguments."""
        async with aiohttp.ClientSession() as session:
            if args.mtf:
                await self.run_mtf(session)
            elif args.days:
                await self.run_historical(session, args.days, args.export)
            else:
                await self.run_snapshot(session, args.json)

    async def run_snapshot(self, session: aiohttp.ClientSession, as_json: bool):
        tasks = []
        for metric_name, config in self.sources_config.items():
            fetcher = FetcherFactory.create(metric_name, config)
            tasks.append(fetcher.fetch(session))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        scored_metrics: List[ScoredMetric] = []
        for i, res in enumerate(results):
            metric_name = list(self.sources_config.keys())[i]
            if isinstance(res, Exception):
                logger.error("Metric fetch failed", metric=metric_name, error=str(res))
                continue
            if res:
                scored = self.analyzer.score_metric(res)
                scored_metrics.append(scored)

        if not scored_metrics:
            logger.critical("No data collected")
            print(f"{RED}[CRITICAL] No data collected. Aborting.{RESET}")
            return

        analysis = calculate_regime(scored_metrics)
        if as_json:
            # Handle datetime serialization for JSON
            print(json.dumps(analysis, indent=2, default=str))
        else:
            self.display_report(analysis)

    async def run_historical(self, session: aiohttp.ClientSession, days: int, export_path: str = None):
        print(f"\n{BOLD}### HISTORICAL REGIME ANALYSIS ({days} DAYS) ###{RESET}")
        tasks = []
        metric_names = list(self.sources_config.keys())
        for name in metric_names:
            config = self.sources_config[name]
            fetcher = FetcherFactory.create(name, config)
            tasks.append(fetcher.fetch_history(session, days))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics_map = {}
        for i, res in enumerate(results):
            name = metric_names[i]
            if isinstance(res, Exception):
                logger.error("Historical fetch failed", metric=name, error=str(res))
                metrics_map[name] = []
            else:
                metrics_map[name] = res

        history = analyze_history(metrics_map, self.analyzer)
        
        if export_path:
            self.export_history(history, export_path)
            print(f"\n{GREEN}{BOLD}Exported historical results to {export_path}{RESET}")
        else:
            print(f"\n{BOLD}Date       | Regime               | Score{RESET}")
            print("-" * 45)
            for day in history:
                print(f"{day['timestamp']} | {day['label']:20} | {day['total_score']:.2f}")
            print("-" * 45 + "\n")

    async def run_mtf(self, session: aiohttp.ClientSession):
        print(f"\n{BOLD}### MULTI-TIMEFRAME CONFLUENCE DASHBOARD ###{RESET}")
        tasks = []
        metric_names = list(self.sources_config.keys())
        for name in metric_names:
            config = self.sources_config[name]
            fetcher = FetcherFactory.create(name, config)
            tasks.append(fetcher.fetch_history(session, 30))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        metrics_map = {}
        for i, res in enumerate(results):
            name = metric_names[i]
            if isinstance(res, Exception):
                logger.error("MTF Historical fetch failed", metric=name, error=str(res))
                metrics_map[name] = []
            else:
                metrics_map[name] = res

        from src.analyzer import analyze_mtf
        results = analyze_mtf(metrics_map, self.analyzer)
        self.display_mtf_report(results)

    def display_mtf_report(self, results: Dict[str, Any]):
        dash_data = []
        for horizon in ['daily', 'weekly', 'monthly']:
            res = results[horizon]
            label = res['label']
            color = GREEN if label == "BULL" else RED if "BEAR" in label else YELLOW
            dash_data.append([horizon.upper(), f"{color}{BOLD}{label}{RESET}", res['total_score'], res['confidence']])
        
        df = pd.DataFrame(dash_data, columns=["Horizon", "Regime", "Score", "Conf"])
        print("\n" + df.to_string(index=False))
        
        print(f"\n{BOLD}MACRO THESIS:{RESET}")
        print(f"| {results['macro_thesis']}\n")
        print("-" * 50 + "\n")

    def export_history(self, history: List[dict], filename: str):
        if filename.endswith('.json'):
            with open(filename, 'w') as f:
                json.dump(history, f, indent=2, default=str)
        else:
            import csv
            if not history: return
            csv_data = []
            for entry in history:
                row = {
                    "timestamp": entry["timestamp"],
                    "label": entry["label"],
                    "score": entry["total_score"],
                    "confidence": entry["confidence"]
                }
                for m in entry.get("breakdown", []):
                    row[f"score_{m['metric']}"] = m["score"]
                    row[f"raw_{m['metric']}"] = m["raw_value"]
                csv_data.append(row)
            
            keys = csv_data[0].keys()
            with open(filename, 'w', newline='') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(csv_data)

    def display_report(self, analysis: dict):
        label = analysis['label']
        color = GREEN if label == "BULL" else RED if label == "BEAR" else YELLOW
        
        print(f"\n{'='*50}")
        print(f"** {BOLD}BITCOIN MARKET REGIME:{RESET} {color}{BOLD}{label}{RESET} **")
        print(f"** {BOLD}CONFIDENCE:{RESET}      {analysis['confidence']} **")
        print(f"** {BOLD}TOTAL SCORE:{RESET}     {analysis['total_score']} **")
        print(f"** {BOLD}TIMESTAMP:{RESET}       {analysis['timestamp']} **")
        print(f"{'='*50}\n")
        
        table_data = []
        has_fallbacks = False
        for m in analysis['breakdown']:
            name = m['metric']
            if m.get('is_fallback'):
                name += " [*]"
                has_fallbacks = True
            table_data.append([name, m['score'], m['raw_value'], m['confidence']])

        df = pd.DataFrame(table_data)
        df.columns = ["Indicator", "Score", "Raw", "Conf"]
        print(df.to_string(index=False))
        
        if has_fallbacks:
            print(f"\n{BOLD}[*] Primary source failed, data retrieved via Backup Tier.{RESET}")
        print(f"\n{'-'*50}\n")

def print_help_metrics():
    print(f"\n{BOLD}INDICATOR REFERENCE GUIDE{RESET}")
    print("-" * 50)
    for metric, hint in METRIC_HINTS.items():
        print(f"{BOLD}{metric.replace('_', ' ').title()}:{RESET}")
        print(f"  {hint}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bitcoin Market Regime Analysis Engine (Async)")
    parser.add_argument("--json", action="store_true", help="Output results as raw JSON")
    parser.add_argument("--help-metrics", action="store_true", help="Show explanation of metrics")
    parser.add_argument("--days", type=int, help="Number of days for historical analyst")
    parser.add_argument("--mtf", action="store_true", help="Launch Multi-Timeframe Confluence Dashboard")
    parser.add_argument("--export", type=str, help="Filename to export historical results (csv/json)")
    parser.add_argument("--sources", default="config/sources.yaml", help="Path to sources.yaml")
    parser.add_argument("--thresholds", default="config/thresholds.yaml", help="Path to thresholds.yaml")
    
    args = parser.parse_args()

    if args.help_metrics:
        print_help_metrics()
        sys.exit(0)
    
    try:
        cli = MarketRegimeCLI(args.sources, args.thresholds)
        asyncio.run(cli.run(args))
    except Exception as e:
        logger.critical("Application Crash", error=str(e))
        print(f"{RED}[CRITICAL] Application Crash: {e}{RESET}")
        sys.exit(1)
