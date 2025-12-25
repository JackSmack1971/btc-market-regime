import aiohttp
from typing import Any, List, Optional
from datetime import datetime
from .base import BaseFetcher, SafeNetworkClient
from ..models import MetricData

class FundingRateFetcher(BaseFetcher):
    """Fetcher for Perpetual Funding Rates (Binance/Gecko)."""
    def parse_primary(self, data: Any) -> float:
        if not data or not isinstance(data, list):
            raise ValueError("Invalid Binance response format")
        return float(data[-1].get('lastFundingRate', 0.0))

    def parse_history(self, data: Any) -> List[MetricData]:
        if not isinstance(data, list): return []
        return [
            MetricData(
                metric_name=self.metric_name,
                value=float(item.get('lastFundingRate', 0.0)),
                timestamp=datetime.fromtimestamp(int(item.get('time', 0)) / 1000),
                source="primary"
            )
            for item in data
        ]

    async def get_backup(self, session: aiohttp.ClientSession) -> float:
        try:
            data = await SafeNetworkClient.get(session, "https://api.coingecko.com/api/v3/derivatives")
            if not isinstance(data, list): return 0.0
            for item in data:
                if item.get('index_id') == 'BTC':
                    return float(item.get('funding_rate', 0.0))
        except Exception:
            pass
        return 0.0

class OpenInterestFetcher(BaseFetcher):
    """Fetcher for Aggregate Open Interest."""
    def parse_primary(self, data: Any) -> float:
        if not data or not isinstance(data, list):
            raise ValueError("Invalid Open Interest data")
        
        total_oi_btc = 0.0
        count = 0
        for item in data:
            if item.get('index_id') == 'BTC':
                oi_usd = item.get('open_interest')
                price = item.get('price')
                if oi_usd and price and float(price) > 0:
                    total_oi_btc += float(oi_usd) / float(price)
                    count += 1
        
        if count == 0:
            raise ValueError("No BTC Open Interest data found")
        return total_oi_btc

    def parse_history(self, data: Any) -> List[MetricData]:
        # Proxy handled by BaseFetcher fallback
        return []

    async def get_backup(self, session: aiohttp.ClientSession) -> float:
        return 0.0
