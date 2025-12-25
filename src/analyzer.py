from typing import List, Dict, Any
import yaml
from datetime import datetime
from abc import ABC, abstractmethod
from .models import ScoredMetric, MetricData
from .utils import logger

class ScoringStrategy(ABC):
    """Abstract base for indicator scoring algorithms."""
    @abstractmethod
    def score(self, value: float, t: Dict[str, Any]) -> float:
        pass

class ThresholdScorer(ScoringStrategy):
    """Signals based on absolute thresholds (High = Bullish)."""
    def score(self, value: float, t: Dict[str, Any]) -> float:
        if value > t.get('bull', float('inf')): return 1.0
        if value < t.get('bear', float('-inf')): return -1.0
        return 0.0

class InverseThresholdScorer(ScoringStrategy):
    """Signals based on absolute thresholds (Low = Bullish, e.g. MVRV)."""
    def score(self, value: float, t: Dict[str, Any]) -> float:
        if value < t.get('bull', float('-inf')): return 1.0
        if value > t.get('bear', float('inf')): return -1.0
        return 0.0

class MultiplierScorer(ScoringStrategy):
    """Signals based on historical multipliers (e.g. Hash Rate)."""
    def score(self, value: float, t: Dict[str, Any]) -> float:
        if value > t.get('bull_multiplier', float('inf')): return 1.0
        if value < t.get('bear_multiplier', float('-inf')): return -1.0
        return 0.0

class MomentumScorer(ScoringStrategy):
    """Signals based on trend momentum (e.g. Active Addresses)."""
    def score(self, value: float, t: Dict[str, Any]) -> float:
        if value > t.get('bull_mom', float('inf')): return 1.0
        if value < t.get('bear_mom', float('-inf')): return -1.0
        return 0.0

class RegimeAnalyzer:
    """Analyzes market data using a Strategy Pattern for scoring logic."""

    def __init__(self, thresholds_path: str):
        with open(thresholds_path, 'r') as f:
            self.config = yaml.safe_load(f)
        self.thresholds = self.config['metrics']
        
        # Strategy Registry
        self._strategies = {
            "fear_greed_index": ThresholdScorer(),
            "perpetual_funding_rates": ThresholdScorer(),
            "mvrv_ratio": InverseThresholdScorer(),
            "rsi": InverseThresholdScorer(),
            "hash_rate": MultiplierScorer(),
            "exchange_net_flows": MultiplierScorer(),
            "active_addresses": MomentumScorer(),
            "open_interest": MomentumScorer(),
        }

    def score_metric(self, data: MetricData) -> ScoredMetric:
        name = data.metric_name
        threshold_key = "rsi" if name == "price_data" else name
        
        if data.source == "failed":
             return ScoredMetric(
                metric_name=name, score=0.0, raw_value=0.0,
                confidence="LOW", reason="source_failed"
            )

        t = self.thresholds.get(threshold_key)
        strategy = self._strategies.get(threshold_key)
        
        if not t or not strategy:
            return ScoredMetric(
                metric_name=name, score=0.0, raw_value=data.value,
                confidence="LOW", reason="missing_config"
            )

        weight = t.get('weight', 1.0)
        base_score = strategy.score(data.value, t)

        confidence = "HIGH" if data.source == "primary" else "MEDIUM"
        is_fallback = (data.source == "backup")
        
        return ScoredMetric(
            metric_name=name,
            score=base_score * weight,
            raw_value=data.value,
            confidence=confidence,
            timestamp=data.timestamp,
            is_fallback=is_fallback
        )

def analyze_history(metrics_map: Dict[str, List[MetricData]], analyzer: RegimeAnalyzer) -> List[Dict[str, Any]]:
    """Aligns multi-source time-series data and produces a historical regime series.
    
    Args:
        metrics_map: Dictionary mapping metric names to lists of historical data.
        analyzer: The RegimeAnalyzer instance to use for scoring.
        
    Returns:
        List[Dict]: A list of historical regime analysis results, one per day.
    """
    # 1. Group by Date (YYYY-MM-DD)
    date_bins: Dict[str, List[MetricData]] = {}
    for name, data_points in metrics_map.items():
        for point in data_points:
            date_str = point.timestamp.strftime('%Y-%m-%d')
            if date_str not in date_bins: date_bins[date_str] = []
            date_bins[date_str].append(point)
            
    # 2. Score and Aggregate for each Day
    historical_results = []
    # Sort dates to ensure chronological output
    sorted_dates = sorted(date_bins.keys())
    
    for date in sorted_dates:
        daily_metrics = date_bins[date]
        scored_metrics = [analyzer.score_metric(m) for m in daily_metrics]
        
        # Aggregate using existing calculate_regime logic
        day_analysis = calculate_regime(scored_metrics)
        # Force the timestamp to the bin date for consistency
        day_analysis['timestamp'] = date
        historical_results.append(day_analysis)
        
    return historical_results

def analyze_mtf(metrics_map: Dict[str, List[MetricData]], analyzer: RegimeAnalyzer) -> Dict[str, Any]:
    """Produces a Multi-Timeframe analysis (Daily, Weekly, Monthly).
    
    Args:
        metrics_map: Dictionary mapping metric names to lists of historical data (at least 30 days recommended).
        analyzer: The RegimeAnalyzer instance.
        
    Returns:
        Dict: Contains 'daily', 'weekly', 'monthly' regime results and a 'macro_thesis'.
    """
    now = datetime.now()
    
    def get_regime_for_range(days: int) -> Dict[str, Any]:
        cutoff = now - timedelta(days=days)
        aggregated_metrics = []
        
        for name, points in metrics_map.items():
            # Fix: Ensure timezone compatibility for comparison
            def is_naive(dt):
                return dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None

            valid_points = []
            for p in points:
                p_ts = p.timestamp
                c_ts = cutoff
                # If one is naive and other is aware, force naive (simplest for internal alignment)
                if is_naive(p_ts) != is_naive(c_ts):
                    p_ts = p_ts.replace(tzinfo=None)
                
                if p_ts >= c_ts:
                    valid_points.append(p)

            if not valid_points: continue
            
            # Simple average aggregation for the timeframe
            avg_val = sum(p.value for p in valid_points) / len(valid_points)
            # Create a proxy MetricData for scoring
            proxy = MetricData(metric_name=name, value=avg_val, timestamp=now, source="primary")
            aggregated_metrics.append(analyzer.score_metric(proxy))
            
        return calculate_regime(aggregated_metrics)

    daily = get_regime_for_range(1)
    weekly = get_regime_for_range(7)
    monthly = get_regime_for_range(30)
    
    # Macro Thesis Logic
    labels = [daily['label'], weekly['label'], monthly['label']]
    if all(l == "BULL" for l in labels):
        thesis = "FULL BULLISH CONFLUENCE: High-conviction uptrend across all horizons."
    elif all(l == "BEAR" for l in labels):
        thesis = "FULL BEARISH CONFLUENCE: Systemic downtrend. Extreme caution advised."
    elif daily['label'] == "BULL" and "BEAR" in labels:
        thesis = "RELIEF RALLY: Daily bullishness fighting against macro bearish pressure."
    elif daily['label'] == "BEAR" and "BULL" in labels:
        thesis = "MACRO CORRECTION: Near-term pull-back in a larger bullish trend."
    else:
        thesis = "MIXED SIGNALS: Market is in a transitional state without clear timeframe alignment."

    return {
        "daily": daily,
        "weekly": weekly,
        "monthly": monthly,
        "macro_thesis": thesis
    }

from datetime import timedelta
def calculate_regime(scored_metrics: List[ScoredMetric]) -> Dict[str, Any]:
    """Aggregates individual metric scores into a final market regime verdict."""
    if not scored_metrics:
        return {"total_score": 0.0, "label": "DATA UNAVAILABLE", "breakdown": []}

    total_score = sum(m.score for m in scored_metrics)
    
    low_confidence_pct = sum(1 for m in scored_metrics if m.confidence == "LOW") / len(scored_metrics)
    overall_confidence = "HIGH" if low_confidence_pct < 0.3 else "MEDIUM"
    if low_confidence_pct > 0.6: overall_confidence = "LOW"
    
    if total_score > 3: label = "BULL"
    elif total_score < -3: label = "BEAR"
    else: label = "SIDEWAYS/TRANSITIONAL"

    breakdown = [
        {
            "metric": m.metric_name,
            "score": round(m.score, 2),
            "raw_value": round(m.raw_value, 4),
            "confidence": m.confidence,
            "is_fallback": m.is_fallback
        }
        for m in scored_metrics
    ]

    return {
        "engine_version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "total_score": round(total_score, 2),
        "label": label,
        "confidence": overall_confidence,
        "breakdown": breakdown
    }
