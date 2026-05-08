from fastapi import Depends

from core.auth import verify_api_key
from core.rate_limit import rate_limiter


async def get_api_key_with_rate_limit(api_key: str = Depends(verify_api_key)) -> str:
    """
    Dependency that verifies API key and checks rate limit.

    Args:
        api_key: Validated API key from auth dependency

    Returns:
        The API key if all checks pass
    """
    await rate_limiter.check_rate_limit(api_key)
    return api_key
