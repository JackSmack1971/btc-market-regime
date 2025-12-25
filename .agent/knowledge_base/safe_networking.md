# Safe Networking Wrapper Pattern

## Context
Use this pattern as a standard interface for all external HTTP requests in a production-grade analytical tool.

## Problem
Ad-hoc `requests.get()` calls often lack consistent timeouts, user-agents, and rate-limiting, leading to unexpected blocks or hanging processes.

## Solution
Wrap network calls in a "Safe Client" that enforces global defensive standards.

### Structural Skeleton
```python
class SafeNetworkClient:
    USER_AGENT = "MyProject/1.0"
    TIMEOUT = 5

    @staticmethod
    def get(url, params=None):
        headers = {"User-Agent": SafeNetworkClient.USER_AGENT}
        response = requests.get(url, headers=headers, params=params, timeout=SafeNetworkClient.TIMEOUT)
        response.raise_for_status()
        time.sleep(1) # Injected rate limit
        return response.json()
```

## Gotchas
- **Global Sleep**: A hard `time.sleep()` is simple but can slow down many-threaded apps. For high-scale systems, use token-bucket or leaky-bucket rate limiting.
- **Timeout Extremes**: 5 seconds is good for most crypto APIs, but some RPC calls or large datasets (e.g., 365-day historicals) might require dynamic timeouts.
