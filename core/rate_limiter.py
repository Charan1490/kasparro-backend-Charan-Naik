"""Rate limiting implementation using token bucket algorithm."""
import time
from threading import Lock
from typing import Dict


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self, rate_limit: int):
        """
        Initialize rate limiter.
        
        Args:
            rate_limit: Maximum requests per minute
        """
        self.rate_limit = rate_limit
        self.tokens = float(rate_limit)
        self.last_update = time.time()
        self.lock = Lock()
    
    def acquire(self, tokens: int = 1) -> bool:
        """
        Acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            True if tokens acquired, False otherwise
        """
        with self.lock:
            now = time.time()
            
            # Refill tokens based on time passed
            time_passed = now - self.last_update
            self.tokens = min(
                self.rate_limit,
                self.tokens + (time_passed * self.rate_limit / 60.0)
            )
            self.last_update = now
            
            # Check if enough tokens available
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def wait(self, tokens: int = 1) -> None:
        """
        Wait until tokens are available.
        
        Args:
            tokens: Number of tokens to wait for
        """
        while not self.acquire(tokens):
            time.sleep(0.1)


class RateLimiterRegistry:
    """Registry for managing multiple rate limiters."""
    
    def __init__(self):
        """Initialize registry."""
        self.limiters: Dict[str, RateLimiter] = {}
        self.lock = Lock()
    
    def get_limiter(self, source: str, rate_limit: int) -> RateLimiter:
        """
        Get or create rate limiter for source.
        
        Args:
            source: Data source name
            rate_limit: Rate limit for the source
            
        Returns:
            RateLimiter instance
        """
        with self.lock:
            if source not in self.limiters:
                self.limiters[source] = RateLimiter(rate_limit)
            return self.limiters[source]


# Global registry
rate_limiter_registry = RateLimiterRegistry()
