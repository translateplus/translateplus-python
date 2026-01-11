"""Custom exceptions for TranslatePlus client."""


class TranslatePlusError(Exception):
    """Base exception for all TranslatePlus errors."""
    pass


class TranslatePlusAPIError(TranslatePlusError):
    """Exception raised for API errors."""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class TranslatePlusAuthenticationError(TranslatePlusAPIError):
    """Exception raised for authentication errors (401, 403)."""
    pass


class TranslatePlusRateLimitError(TranslatePlusAPIError):
    """Exception raised for rate limit errors (429)."""
    pass


class TranslatePlusInsufficientCreditsError(TranslatePlusAPIError):
    """Exception raised for insufficient credits (402)."""
    pass


class TranslatePlusValidationError(TranslatePlusError):
    """Exception raised for validation errors."""
    pass
