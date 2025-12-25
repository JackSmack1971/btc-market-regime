import requests
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from abc import ABC, abstractmethod

from ..models import MetricData
from ..utils import logger, CircuitBreaker, RED, RESET

# Global Circuit Breaker for the package
cb = CircuitBreaker()

class SafeNetworkClient:
    """Defensive networking wrapper with rate limiting and timeouts.
    
    This class ensures all external requests adhere to safe engineering
    standards, including custom User-Agent headers, hard timeouts, and
    forced rate limiting to avoid API bans.
    """
    USER_AGENT = "BitcoinRegimeAnalyzer/1.0 (Senior Engineering Edition)"
    TIMEOUT = 5  # Hard 5-second timeout

    @staticmethod
    def get(url: str, params: Optional[Dict] = None) -> Any:
        """Performs a safe GET request with automatic rate limiting.

        Args:
            url: The endpoint to query.
            params: Optional query parameters.

        Returns:
            Any: The JSON-decoded response body.

        Raises:
            requests.exceptions.RequestException: If the network call fails.
        """
        try:
            headers = {"User-Agent": SafeNetworkClient.USER_AGENT}
            response = requests.get(url, headers=headers, params=params, timeout=SafeNetworkClient.TIMEOUT)
            response.raise_for_status()
            
            # Rate limiting: 1s sleep after every successful call
            time.sleep(1)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Network request failed", url=url, error=str(e))
            raise

    @staticmethod
    def post(url: str, json_data: Dict) -> Any:
        """Performs a safe POST request.

        Args:
            url: The endpoint to query.
            json_data: The dictionary to send as JSON payload.

        Returns:
            Any: The JSON-decoded response body.
        """
        try:
            headers = {"User-Agent": SafeNetworkClient.USER_AGENT}
            response = requests.post(url, headers=headers, json=json_data, timeout=SafeNetworkClient.TIMEOUT)
            response.raise_for_status()
            
            time.sleep(1)
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("RPC request failed", url=url, error=str(e))
            raise

def alchemy_rpc(method: str, params: List = []) -> Any:
    """Executes a Bitcoin JSON-RPC call via an Alchemy-compatible provider.

    Args:
        method: The RPC method name (e.g., 'getblockcount').
        params: List of arguments for the RPC method.

    Returns:
        Any: The RPC response payload.
    """
    URL = "https://btc-mainnet.g.alchemy.com/v2/your-api-key" # Placeholder
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params
    }
    return SafeNetworkClient.post(URL, payload)

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

    @abstractmethod
    def parse_primary(self, data: Any) -> float:
        """Parses the raw JSON from the primary source."""
        pass
    
    @abstractmethod
    def parse_history(self, data: Any) -> List[MetricData]:
        """Parses multiple data points from the primary source."""
        pass

    @abstractmethod
    def get_backup(self) -> float:
        """Retrieves data from the backup source."""
        pass

    def fetch_history(self, days: int) -> List[MetricData]:
        """Fetches historical data points.
        
        Default implementation attempts primary historical query, 
        then falls back to latest value if history is unavailable.
        """
        try:
            logger.info("Tier 1: Fetching history", metric=self.metric_name, days=days)
            # This expects subclasses to handle the historical URL/params
            data = SafeNetworkClient.get(self.primary_url)
            return self.parse_history(data)
        except Exception as e:
            logger.warning("Historical fetch failed, providing latest as proxy", metric=self.metric_name, error=str(e))
            latest = self.fetch()
            return [latest] if latest else []

    def fetch(self) -> Optional[MetricData]:
        """Orchestrates the multi-tier retrieval process."""
        if cb.is_available(f"primary_{self.metric_name}"):
            try:
                logger.info("Tier 1: Attempting primary", metric=self.metric_name)
                data = SafeNetworkClient.get(self.primary_url)
                value = self.parse_primary(data)
                cb.report_success(f"primary_{self.metric_name}")
                return MetricData(
                    metric_name=self.metric_name,
                    value=value,
                    timestamp=datetime.now(),
                    source="primary"
                )
            except Exception as e:
                logger.error("Primary failed", metric=self.metric_name, error=str(e))
                cb.report_failure(f"primary_{self.metric_name}")

        try:
            logger.info("Tier 2: Attempting backup", metric=self.metric_name)
            value = self.get_backup()
            return MetricData(
                metric_name=self.metric_name,
                value=value,
                timestamp=datetime.now(),
                source="backup"
            )
        except Exception as e:
            print(f"{RED}[CRITICAL] All sources failed for {self.metric_name}: {e}{RESET}")
            logger.critical("TOTAL FAILURE", metric=self.metric_name, error=str(e))
            return MetricData(
                metric_name=self.metric_name,
                value=0.0,
                timestamp=datetime.now(),
                source="failed"
            )
