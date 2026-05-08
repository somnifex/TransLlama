import time
from collections import defaultdict
from typing import Dict
from fastapi import Request, HTTPException, status

from core.config import settings


class RateLimiter:
    """Simple in-memory rate limiter using token bucket algorithm"""

    def __init__(self, requests_per_minute: int = None):
        """
        Initialize rate limiter.

        Args:
            requests_per_minute: Maximum requests per minute per key
        """
        self.requests_per_minute = requests_per_minute or settings.rate_limit_requests_per_minute
        self.requests: Dict[str, list] = defaultdict(list)

    async def check_rate_limit(self, api_key: str):
        """
        Check if request is within rate limit.

        Args:
            api_key: API key to check

        Raises:
            HTTPException: If rate limit exceeded
        """
        current_time = time.time()
        minute_ago = current_time - 60

        # Clean up old requests
        self.requests[api_key] = [
            req_time for req_time in self.requests[api_key]
            if req_time > minute_ago
        ]

        # Check rate limit
        if len(self.requests[api_key]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Maximum {self.requests_per_minute} requests per minute.",
            )

        # Add current request
        self.requests[api_key].append(current_time)


# Global rate limiter instance
rate_limiter = RateLimiter()
