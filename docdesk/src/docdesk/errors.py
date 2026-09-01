"""Error classification for the Document Intelligence & Support Application."""
import anthropic

import random
import time

# Transient: safe to retry with backoff (E8 implements the actual retry loop).
RETRYABLE = (
    anthropic.RateLimitError,        # 429
    anthropic.InternalServerError,   # 500 / 529 overloaded
    anthropic.APITimeoutError,       # request timed out
    anthropic.APIConnectionError,    # network dropped
)

# Permanent: caller must fix the request/credentials. Never retry.
FIX_IT = (
    anthropic.BadRequestError,       # 400
    anthropic.AuthenticationError,   # 401
    anthropic.PermissionDeniedError, # 403
    anthropic.NotFoundError,         # 404
)


def is_retryable(exc: Exception) -> bool:
    """True if this error is transient and worth retrying with backoff."""
    return isinstance(exc, RETRYABLE)

def with_backoff(fn, *, max_attempts: int = 5, base: float = 1.0, cap: float = 60.0):
    """Call fn(), retrying ONLY retryable errors with exponential backoff + jitter.

    - Fix-it errors (400/401/403/404) are re-raised immediately (no retry).
    - Transient errors (429/5xx/timeout/connection) back off: 1, 2, 4, 8... capped.
    - After max_attempts, the last error is raised so the caller sees a clear failure.
    """
    for attempt in range(max_attempts):
        try:
            return fn()
        except Exception as e:
            if not is_retryable(e) or attempt == max_attempts - 1:
                raise
            wait = min(cap, base * (2 ** attempt))
            wait += random.uniform(0, wait * 0.1)   # jitter
            time.sleep(wait)