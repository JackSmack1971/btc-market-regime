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
    """Manages service availability by tracking consecutive failures."""
    def __init__(self, failure_threshold: int = 3, recovery_timeout: int = 300):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = {}  
        self.last_failure_time = {}  
        self.state = {}  

    def is_available(self, name: str) -> bool:
        state = self.state.get(name, "CLOSED")
        if state == "CLOSED":
            return True
        last_fail = self.last_failure_time.get(name, 0)
        if time.time() - last_fail > self.recovery_timeout:
            self.state[name] = "HALF-OPEN"
            return True
        return False

    def report_failure(self, name: str):
        self.failures[name] = self.failures.get(name, 0) + 1
        if self.failures[name] >= self.failure_threshold:
            self.state[name] = "OPEN"
            self.last_failure_time[name] = time.time()
            logger.error("Circuit breaker opened", name=name, state="OPEN")

    def report_success(self, name: str):
        self.failures[name] = 0
        self.state[name] = "CLOSED"

# Retry Decorator
def retry_with_backoff(max_attempts: int = 3, base_delay: int = 2, exceptions: tuple = (Exception,)):
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

# Expose sub-modules
from .health import health_tracker
from .alerts import alert_manager

__all__ = [
    "logger", "RED", "RESET", "CircuitBreaker", "retry_with_backoff",
    "AppError", "NetworkError", "TimeoutError", "ParseError", 
    "RateLimitError", "AuthError", "MaxRetriesExceeded",
    "health_tracker", "alert_manager"
]
