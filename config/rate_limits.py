# FilePath: config/rate_limits.py

import time
from typing import Dict, Optional
from dataclasses import dataclass
from threading import Lock


@dataclass
class RateLimitConfig:
    """Rate limit configuration for different services."""

    requests_per_minute: int
    burst_limit: int
    retry_after: float
    max_retries: int


class RateLimiter:
    """Thread-safe rate limiter implementation."""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests = []
        self.lock = Lock()

    def can_proceed(self) -> bool:
        """Check if a request can proceed based on rate limits."""
        with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            self.requests = [
                req_time for req_time in self.requests if now - req_time < 60
            ]

            # Check if we can make a new request
            if len(self.requests) < self.config.requests_per_minute:
                self.requests.append(now)
                return True
            return False

    def wait_if_needed(self) -> None:
        """Wait if rate limit is exceeded."""
        if not self.can_proceed():
            time.sleep(self.config.retry_after)


# Rate limit configurations for different LLM providers
RATE_LIMITS: Dict[str, RateLimitConfig] = {
    "claude": RateLimitConfig(
        requests_per_minute=50, burst_limit=5, retry_after=2.0, max_retries=3
    ),
    "openai": RateLimitConfig(
        requests_per_minute=60, burst_limit=10, retry_after=1.0, max_retries=3
    ),
    "default": RateLimitConfig(
        requests_per_minute=30, burst_limit=3, retry_after=3.0, max_retries=2
    ),
}


class RateLimitManager:
    """Manages rate limiters for different services."""

    def __init__(self):
        self._limiters: Dict[str, RateLimiter] = {}

    def get_limiter(self, service: str) -> RateLimiter:
        """Get rate limiter for a service."""
        if service not in self._limiters:
            config = RATE_LIMITS.get(service, RATE_LIMITS["default"])
            self._limiters[service] = RateLimiter(config)
        return self._limiters[service]

    def wait_if_needed(self, service: str) -> None:
        """Wait if rate limit is exceeded for a service."""
        limiter = self.get_limiter(service)
        limiter.wait_if_needed()


# Global rate limit manager instance
rate_limit_manager = RateLimitManager()
