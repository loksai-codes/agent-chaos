"""Errors agents and resilience stages can distinguish."""


class ToolError(Exception):
    """Base class for simulated tool failures."""


class ToolTimeout(ToolError):
    """A tool exceeded its virtual call timeout."""


class TransientError(ToolError):
    """A retryable transient backend failure."""


class RateLimited(ToolError):
    """A rate-limit failure with a virtual retry delay."""

    def __init__(self, retry_after: float) -> None:
        self.retry_after = retry_after
        super().__init__(f"Rate limited; retry after {retry_after:g}s")


class ValidationFailed(ToolError):
    """A tool response failed schema or invariant validation."""


class CircuitOpen(ToolError):
    """A circuit breaker is rejecting calls."""


class BudgetExceeded(ToolError):
    """An agent or execution budget was exhausted."""
