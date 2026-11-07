class Week8Error(Exception):
    """Base class for project errors."""


class ConfigError(Week8Error):
    """Missing or invalid configuration."""


class RetrievalError(Week8Error):
    """Vector store problems."""


class TransientError(Week8Error):
    """Temporary failure (timeout, rate limit) - safe to retry."""


class PermanentError(Week8Error):
    """Bad input / logic error - retrying will not help."""
