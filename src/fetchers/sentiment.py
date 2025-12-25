import aiohttp
from typing import Any, List
from datetime import datetime
import time
from .base import BaseFetcher, SafeNetworkClient, logger
from ..models import MetricData

class FearGreedFetcher(BaseFetcher):
    """Fetcher for the Alternative.me Fear & Greed Index."""
    def parse_primary(self, data: Any) -> float:
        fng_data = data.get('data')
        if not fng_data or not isinstance(fng_data, list):
            raise ValueError("Invalid Alternative.me response format")
        return float(fng_data[0].get('value', 50))

    def parse_history(self, data: Any) -> List[MetricData]:
        fng_data = data.get('data', [])
        return [
            MetricData(
                metric_name=self.metric_name,
                value=float(item.get('value', 50)),
                timestamp=datetime.fromtimestamp(int(item.get('timestamp', time.time()))),
                source="primary"
            )
            for item in fng_data
        ]

    async def fetch_history(self, session: aiohttp.ClientSession, days: int) -> List[MetricData]:
        url = f"{self.primary_url}?limit={days}"
        try:
            data = await SafeNetworkClient.get(session, url)
            return self.parse_history(data)
        except Exception:
            return await super().fetch_history(session, days)

    async def get_backup(self, session: aiohttp.ClientSession) -> float:
        logger.warning("Using volatility-based backup for Fear & Greed")
        return 50.0
