"""Custom exceptions raised by web routes — caught globally in main.py."""


class WebAuthRequired(Exception):
    """Raised when a web route requires authentication but none is present."""
    pass


class WebForbidden(Exception):
    """Raised when the current user lacks the required role."""
    def __init__(self, message: str = "Access denied."):
        self.message = message
        super().__init__(message)
