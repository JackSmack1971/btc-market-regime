import pandas as pd
from typing import Any, List
from datetime import datetime
from .base import BaseFetcher, SafeNetworkClient, logger
from ..models import MetricData

class MVRVFetcher(BaseFetcher):
    """Fetcher for MVRV Ratio (CoinMetrics/Blockchain)."""
    def parse_primary(self, data: Any) -> float:
        mvrv_data = data.get('data')
        if not mvrv_data or not isinstance(mvrv_data, list):
            raise ValueError("Invalid CoinMetrics response")
        return float(mvrv_data[0].get('CapMVRVCur', 0.0))

    def parse_history(self, data: Any) -> List[MetricData]:
        mvrv_data = data.get('data', [])
        return [
            MetricData(
                metric_name=self.metric_name,
                value=float(item.get('CapMVRVCur', 0.0)),
                timestamp=datetime.fromisoformat(item.get('time').replace('Z', '+00:00')),
                source="primary"
            )
            for item in mvrv_data
        ]

    def fetch_history(self, days: int) -> List[MetricData]:
        # Implementation inherits super() and uses blockchain backup if primary lacks history params
        return super().fetch_history(days)

    def get_backup(self) -> float:
        try:
            data = SafeNetworkClient.get(self.backup_source)
            values = data.get('values')
            if not values or not isinstance(values, list): return 0.0
            return float(values[-1].get('y', 0.0))
        except Exception:
            return 0.0

class RSIDataFetcher(BaseFetcher):
    """Fetcher for 14-day RSI (CoinGecko)."""
    def parse_primary(self, data: Any) -> float:
        prices_raw = data.get('prices')
        if not prices_raw or not isinstance(prices_raw, list) or len(prices_raw) < 15:
            return 50.0
        
        prices = [p[1] for p in prices_raw if isinstance(p, list) and len(p) >= 2]
        if len(prices) < 15: return 50.0
            
        series = pd.Series(prices)
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        
        last_loss = loss.iloc[-1]
        if pd.isna(last_loss) or last_loss == 0:
            return 100.0 if (gain.iloc[-1] > 0) else 50.0
            
        rs = gain.iloc[-1] / last_loss
        return float(100 - (100 / (1 + rs)))

    def parse_history(self, data: Any) -> List[MetricData]:
        # RSI history requires full 14d window per point.
        # MVP: Return the latest RSI as a proxy for the series.
        latest = self.fetch()
        return [latest] if latest else []

    def get_backup(self) -> float:
        return 50.0
