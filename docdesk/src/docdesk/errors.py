"""Error classification for the Document Intelligence & Support Application."""
import anthropic

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