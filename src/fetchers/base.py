import aiohttp
import asyncio
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from abc import ABC, abstractmethod

from ..models import MetricData
from ..utils import logger, CircuitBreaker, RED, RESET, health_tracker
from ..cache import cache

# Global Circuit Breaker for the package
cb = CircuitBreaker()

class SafeNetworkClient:
    """Defensive networking wrapper with rate limiting and timeouts (Async)."""
    USER_AGENT = "BitcoinRegimeAnalyzer/1.0 (Senior Engineering Edition)"
    TIMEOUT = 5 

    @staticmethod
    async def get(session: aiohttp.ClientSession, url: str, params: Optional[Dict] = None) -> Any:
        """Performs a safe async GET request."""
        try:
            headers = {"User-Agent": SafeNetworkClient.USER_AGENT}
            async with session.get(url, headers=headers, params=params, timeout=SafeNetworkClient.TIMEOUT) as response:
                response.raise_for_status()
                # Rate limiting simulation: small pause
                await asyncio.sleep(0.5) 
                return await response.json()
        except Exception as e:
            logger.error("Async GET failed", url=url, error=str(e))
            raise

    @staticmethod
    async def post(session: aiohttp.ClientSession, url: str, json_data: Dict) -> Any:
        """Performs a safe async POST request."""
        try:
            headers = {"User-Agent": SafeNetworkClient.USER_AGENT}
            async with session.post(url, headers=headers, json=json_data, timeout=SafeNetworkClient.TIMEOUT) as response:
                response.raise_for_status()
                await asyncio.sleep(0.5)
                return await response.json()
        except Exception as e:
            logger.error("Async POST failed", url=url, error=str(e))
            raise

async def alchemy_rpc(session: aiohttp.ClientSession, method: str, params: List = []) -> Any:
    """Executes a Bitcoin JSON-RPC call asychronously."""
    URL = "https://btc-mainnet.g.alchemy.com/v2/your-api-key"
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    return await SafeNetworkClient.post(session, URL, payload)

class BaseFetcher(ABC):
    """Abstract base class for all metric data fetchers.
    
    Implements the Graduated Fallback Protocol (Primary -> Backup -> Neutral)
    and integrates with the global Circuit Breaker.

    Attributes:
        metric_name (str): Unique identifier for the metric.
        primary_url (str): The tier 1 API endpoint.
        backup_source (str): The tier 2 source (URL or provider name).
    """
    def __init__(self, metric_name: str, config: Dict[str, Any]):
        """Initializes the fetcher with configuration.

        Args:
            metric_name: Name of the metric to fetch.
            config: Source configuration dictionary.
        """
        self.metric_name = metric_name
        self.primary_url = config.get('primary')
        self.backup_source = config.get('backup')
        self.ttl_minutes = config.get('ttl_minutes', 5) # Default 5 min TTL

    @abstractmethod
    def parse_primary(self, data: Any) -> float:
        """Parses the raw JSON from the primary source."""
        pass
    
    @abstractmethod
    def parse_history(self, data: Any) -> List[MetricData]:
        """Parses multiple data points from the primary source."""
        pass

    @abstractmethod
    async def get_backup(self, session: aiohttp.ClientSession) -> float:
        """Retrieves data from the backup source asychronously."""
        pass

    async def fetch_history(self, session: aiohttp.ClientSession, days: int) -> List[MetricData]:
        """Fetches historical data points asychronously."""
        cache_key = f"{self.metric_name}_history_{days}"
        cached_data = cache.get(cache_key, ttl_minutes=self.ttl_minutes)
        if cached_data:
            return cached_data

        start_time = time.time()
        try:
            logger.info("Tier 1: Fetching history (Async)", metric=self.metric_name, days=days)
            data = await SafeNetworkClient.get(session, self.primary_url)
            result = self.parse_history(data)
            latency = (time.time() - start_time) * 1000
            
            if result:
                health_tracker.log_attempt(self.metric_name, "primary", True, latency)
                cache.set(cache_key, result)
            return result
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            health_tracker.log_attempt(self.metric_name, "primary", False, latency, str(e))
            logger.warning("Historical fetch failed (Async), providing latest as proxy", metric=self.metric_name, error=str(e))
            latest = await self.fetch(session)
            return [latest] if latest else []

    async def fetch(self, session: aiohttp.ClientSession) -> Optional[MetricData]:
        """Orchestrates the multi-tier retrieval process asychronously."""
        cache_key = f"{self.metric_name}_latest"
        cached_data = cache.get(cache_key, ttl_minutes=self.ttl_minutes)
        if cached_data:
            return cached_data

        if cb.is_available(f"primary_{self.metric_name}"):
            start_time = time.time()
            try:
                logger.info("Tier 1: Attempting primary (Async)", metric=self.metric_name)
                data = await SafeNetworkClient.get(session, self.primary_url)
                value = self.parse_primary(data)
                cb.report_success(f"primary_{self.metric_name}")
                
                latency = (time.time() - start_time) * 1000
                health_tracker.log_attempt(self.metric_name, "primary", True, latency)
                
                result = MetricData(
                    metric_name=self.metric_name,
                    value=value,
                    timestamp=datetime.now(),
                    source="primary"
                )
                cache.set(cache_key, result)
                return result
            except Exception as e:
                latency = (time.time() - start_time) * 1000
                health_tracker.log_attempt(self.metric_name, "primary", False, latency, str(e))
                logger.error("Primary failed (Async)", metric=self.metric_name, error=str(e))
                cb.report_failure(f"primary_{self.metric_name}")

        start_time = time.time()
        try:
            logger.info("Tier 2: Attempting backup (Async)", metric=self.metric_name)
            value = await self.get_backup(session)
            latency = (time.time() - start_time) * 1000
            health_tracker.log_attempt(self.metric_name, "backup", True, latency)
            
            result = MetricData(
                metric_name=self.metric_name,
                value=value,
                timestamp=datetime.now(),
                source="backup"
            )
            cache.set(cache_key, result)
            return result
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            health_tracker.log_attempt(self.metric_name, "backup", False, latency, str(e))
            print(f"{RED}[CRITICAL] All sources failed for {self.metric_name}: {e}{RESET}")
            logger.critical("TOTAL FAILURE (Async)", metric=self.metric_name, error=str(e))
            return MetricData(
                metric_name=self.metric_name,
                value=0.0,
                timestamp=datetime.now(),
                source="failed"
            )
