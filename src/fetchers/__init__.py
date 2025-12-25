from typing import Dict, Any, Type
from .base import BaseFetcher, SafeNetworkClient, cb
from .sentiment import FearGreedFetcher
from .on_chain import HashRateFetcher, ExchangeNetFlowsFetcher, ActiveAddressFetcher
from .derivatives import FundingRateFetcher, OpenInterestFetcher
from .valuation import MVRVFetcher, RSIDataFetcher

class FetcherFactory:
    """Factory for creating indicator-specific fetcher instances.
    
    This factory centralizes the mapping of metric names to leur 
    respective implementation classes.
    """
    _mapping = {
        "fear_greed_index": FearGreedFetcher,
        "hash_rate": HashRateFetcher,
        "exchange_net_flows": ExchangeNetFlowsFetcher,
        "active_addresses": ActiveAddressFetcher,
        "perpetual_funding_rates": FundingRateFetcher,
        "open_interest": OpenInterestFetcher,
        "mvrv_ratio": MVRVFetcher,
        "price_data": RSIDataFetcher,
    }

    @classmethod
    def create(cls, metric_name: str, config: Dict[str, Any]) -> BaseFetcher:
        """Creates a fetcher instance for the given metric.

        Args:
            metric_name: The metric identifier.
            config: Source configuration for the metric.

        Returns:
            BaseFetcher: The instantiated fetcher.

        Raises:
            ValueError: If the metric name is not recognized.
        """
        fetcher_cls = cls._mapping.get(metric_name)
        if not fetcher_cls:
            raise ValueError(f"Unknown metric: {metric_name}")
        return fetcher_cls(metric_name, config)

__all__ = [
    "FetcherFactory",
    "BaseFetcher",
    "SafeNetworkClient",
    "cb",
    "FearGreedFetcher",
    "HashRateFetcher",
    "ExchangeNetFlowsFetcher",
    "ActiveAddressFetcher",
    "FundingRateFetcher",
    "OpenInterestFetcher",
    "MVRVFetcher",
    "RSIDataFetcher"
]
