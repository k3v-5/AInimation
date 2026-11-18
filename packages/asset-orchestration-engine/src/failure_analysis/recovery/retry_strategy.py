from typing import Dict, Any

class RetryStrategy:
    """Manages retry limits and backoff policies."""
    MAX_ATTEMPTS = 3

    @classmethod
    def can_retry(cls, attempt_count: int, retryable: bool) -> bool:
        return retryable and (attempt_count < cls.MAX_ATTEMPTS)
