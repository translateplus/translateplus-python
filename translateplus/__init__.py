"""
TranslatePlus Python Client Library

Official Python client for TranslatePlus API - Professional translation service
for text, HTML, emails, subtitles, and i18n files in 100+ languages.
"""

from translateplus.client import TranslatePlusClient
from translateplus.exceptions import (
    TranslatePlusError,
    TranslatePlusAPIError,
    TranslatePlusAuthenticationError,
    TranslatePlusRateLimitError,
    TranslatePlusInsufficientCreditsError,
    TranslatePlusValidationError,
)

__version__ = "2.0.4"
__all__ = [
    "TranslatePlusClient",
    "TranslatePlusError",
    "TranslatePlusAPIError",
    "TranslatePlusAuthenticationError",
    "TranslatePlusRateLimitError",
    "TranslatePlusInsufficientCreditsError",
    "TranslatePlusValidationError",
]
