"""
Domain-level errors for agent execution lifecycle.
"""


class ExecutionCancelledError(Exception):
    """
    Raised when an ExecutionScope detects that the execution has been
    cancelled (by external signal or deadline expiry).

    Agents MUST catch this explicitly and NOT via bare `except Exception`.
    They should save final memory state before propagating or returning.
    """
