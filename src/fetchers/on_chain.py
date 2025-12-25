import aiohttp
from typing import Any, List
from datetime import datetime
import time
from .base import BaseFetcher, SafeNetworkClient
from ..models import MetricData

class HashRateFetcher(BaseFetcher):
    """Fetcher for Bitcoin Network Hash Rate."""
    def parse_primary(self, data: Any) -> float:
        values = data.get('values')
        if not values or not isinstance(values, list):
            raise ValueError("Invalid Blockchain.info response format")
        return float(values[-1].get('y', 0))

    def parse_history(self, data: Any) -> List[MetricData]:
        values = data.get('values', [])
        return [
            MetricData(
                metric_name=self.metric_name,
                value=float(item.get('y', 0.0)),
                timestamp=datetime.fromtimestamp(int(item.get('x', time.time()))),
                source="primary"
            )
            for item in values
        ]

    async def fetch_history(self, session: aiohttp.ClientSession, days: int) -> List[MetricData]:
        url = f"{self.primary_url}?timespan={days}days&format=json"
        try:
            data = await SafeNetworkClient.get(session, url)
            return self.parse_history(data)
        except Exception:
            return await super().fetch_history(session, days)

    async def get_backup(self, session: aiohttp.ClientSession) -> float:
        try:
            data = await SafeNetworkClient.get(session, self.backup_source)
            return 1.0 # Progress proxy logic
        except Exception:
            return 0.0

class ExchangeNetFlowsFetcher(BaseFetcher):
    """Fetcher for Exchange Net Flows."""
    def parse_primary(self, data: Any) -> float:
        if not isinstance(data, dict):
            return 0.0
        return float(data.get('netflow', 0.0))

    def parse_history(self, data: Any) -> List[MetricData]:
        # Proxy handled by BaseFetcher fallback
        return []

    async def get_backup(self, session: aiohttp.ClientSession) -> float:
        return 0.0

class ActiveAddressFetcher(BaseFetcher):
    """Fetcher for Active Bitcoin Addresses."""
    def parse_primary(self, data: Any) -> float:
        values = data.get('values')
        if not values or not isinstance(values, list):
            raise ValueError("Invalid Active Address data")
        return float(values[-1].get('y', 0.0))

    def parse_history(self, data: Any) -> List[MetricData]:
        values = data.get('values', [])
        return [
            MetricData(
                metric_name=self.metric_name,
                value=float(item.get('y', 0.0)),
                timestamp=datetime.fromtimestamp(int(item.get('x', time.time()))),
                source="primary"
            )
            for item in values
        ]

    async def fetch_history(self, session: aiohttp.ClientSession, days: int) -> List[MetricData]:
        url = f"{self.primary_url}?timespan={days}days&format=json"
        try:
            data = await SafeNetworkClient.get(session, url)
            return self.parse_history(data)
        except Exception:
            return await super().fetch_history(session, days)

    async def get_backup(self, session: aiohttp.ClientSession) -> float:
        try:
            data = await SafeNetworkClient.get(session, self.backup_source)
            txs = data.get('data', {}).get('transactions_24h')
            return float(txs or 0.0)
        except Exception:
            return 0.0
