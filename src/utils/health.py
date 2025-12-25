import pandas as pd
from dataclasses import dataclass, asdict
from typing import List, Dict
from datetime import datetime

@dataclass
class HealthEntry:
    metric_name: str
    source: str  # 'primary' or 'backup'
    success: bool
    latency_ms: float
    timestamp: datetime
    error: str = ""

class HealthTracker:
    """Tracks fetcher health metrics for the dashboard HUD."""
    
    def __init__(self):
        self._history: List[HealthEntry] = []
        
    def log_attempt(self, metric_name: str, source: str, success: bool, latency_ms: float, error: str = ""):
        entry = HealthEntry(
            metric_name=metric_name,
            source=source,
            success=success,
            latency_ms=latency_ms,
            timestamp=datetime.now(),
            error=error
        )
        self._history.append(entry)
        
    def get_summary(self) -> pd.DataFrame:
        """Returns a summary of fetcher performance."""
        if not self._history:
            return pd.DataFrame()
            
        df = pd.DataFrame([asdict(e) for e in self._history])
        return df

    def get_latest_status(self) -> Dict[str, Dict]:
        """Returns the last success/failure for each metric."""
        status = {}
        for entry in self._history:
            status[entry.metric_name] = {
                "last_source": entry.source,
                "last_success": entry.success,
                "last_latency": entry.latency_ms,
                "last_error": entry.error
            }
        return status

# Global tracker instance
health_tracker = HealthTracker()
