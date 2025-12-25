from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Dict, Any, List

@dataclass
class MetricData:
    """Represents a single data point for a market metric."""
    metric_name: str
    value: float
    timestamp: datetime
    source: str

@dataclass
class ScoredMetric:
    """Represents a metric that has been processed and scored."""
    metric_name: str
    score: float
    raw_value: float
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    timestamp: datetime = datetime.now()
    is_fallback: bool = False

@dataclass
class Regime:
    """Represents the current market regime."""
    label: Literal["BULL", "BEAR", "NEUTRAL"]
    score: float
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    timestamp: datetime = datetime.now()

@dataclass
class HistoricalRegime:
    """Represents a regime verdict for a specific point in time."""
    timestamp: str
    label: str
    score: float
    confidence: str
    metrics: Dict[str, float]
