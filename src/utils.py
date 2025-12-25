import structlog
import time
from typing import Callable, Any, List, Type
from functools import wraps
import logging
import sys

# Structured Logging Setup
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(file=sys.stderr),
    wrapper_class=structlog.BoundLogger,
    cache_logger_on_first_use=True,
)
# Logger Setup
logger = structlog.get_logger()

# ANSI Color Colors
RED = "\033[91m"
RESET = "\033[0m"

# Error Types
class AppError(Exception): pass
class NetworkError(AppError): pass
class TimeoutError(AppError): pass
class ParseError(AppError): pass
class RateLimitError(AppError): pass
class AuthError(AppError): pass
class MaxRetriesExceeded(AppError): pass

# Simple Circuit Breaker
class CircuitBreaker:
    """Manages service availability by tracking consecutive failures.
    
    The breaker transitions through three states:
    - CLOSED: Service is healthy, calls are allowed.
    - OPEN: Service has failed threshold times, calls are blocked.
    - HALF-OPEN: Recovery timeout elapsed, testing one call.

    Attributes:
        failure_threshold (int): Attempts before opening the breaker.
        recovery_timeout (int): Seconds to wait before transitioning to HALF-OPEN.
    """
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 300):
        """Initializes the circuit breaker with custom thresholds.

        Args:
            failure_threshold: Defaults to 3.
            recovery_timeout: Seconds to cooldown. Defaults to 300.
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = {}  # {name: count}
        self.last_failure_time = {}  # {name: timestamp}
        self.state = {}  # {name: "CLOSED" | "OPEN" | "HALF-OPEN"}

    def is_available(self, name: str) -> bool:
        """Checks if the named service is currently available.

        Args:
            name: Identifier for the service/endpoint.

        Returns:
            bool: True if allowed to proceed.
        """
        state = self.state.get(name, "CLOSED")
        if state == "CLOSED":
            return True
        
        last_fail = self.last_failure_time.get(name, 0)
        if time.time() - last_fail > self.recovery_timeout:
            self.state[name] = "HALF-OPEN"
            return True
        
        return False

    def report_failure(self, name: str):
        """Records a service failure and opens breaker if threshold met.

        Args:
            name: Identifier for the failed service.
        """
        self.failures[name] = self.failures.get(name, 0) + 1
        if self.failures[name] >= self.failure_threshold:
            self.state[name] = "OPEN"
            self.last_failure_time[name] = time.time()
            logger.error("Circuit breaker opened", name=name, state="OPEN")

    def report_success(self, name: str):
        """Resets the failure counter and closes the breaker.

        Args:
            name: Identifier for the successful service.
        """
        self.failures[name] = 0
        self.state[name] = "CLOSED"

# Retry Decorator (Simplified version of tenacity/custom)
def retry_with_backoff(max_attempts: int = 3, base_delay: int = 2, exceptions: tuple = (Exception,)):
    """A decorator for implementing exponential backoff retry logic.

    Args:
        max_attempts: Number of total attempts before giving up.
        base_delay: Initial wait time in seconds.
        exceptions: Tuple of exception types to trigger a retry.

    Returns:
        Callable: The wrapped function with retry logic.

    Raises:
        MaxRetriesExceeded: If all attempts fail.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_err = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_err = e
                    delay = base_delay * (2 ** attempt)
                    logger.warning("Attempt failed, retrying...", 
                                   func=func.__name__, 
                                   attempt=attempt + 1, 
                                   delay=delay, 
                                   error=str(e))
                    time.sleep(delay)
            raise MaxRetriesExceeded(f"Max retries reached for {func.__name__}: {last_err}")
        return wrapper
    return decorator
