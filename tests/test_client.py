"""Tests for TranslatePlusClient."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import requests

from translateplus import TranslatePlusClient
from translateplus.exceptions import (
    TranslatePlusAuthenticationError,
    TranslatePlusRateLimitError,
    TranslatePlusInsufficientCreditsError,
    TranslatePlusAPIError,
)


class TestTranslatePlusClient(unittest.TestCase):
    """Test cases for TranslatePlusClient."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.api_key = "test-api-key"
        self.client = TranslatePlusClient(api_key=self.api_key)
    
    def tearDown(self):
        """Clean up after tests."""
        self.client.close()
    
    def test_init_with_api_key(self):
        """Test client initialization with API key."""
        client = TranslatePlusClient(api_key="test-key")
        self.assertEqual(client.api_key, "test-key")
        self.assertEqual(client.base_url, "https://api.translateplus.com")
        client.close()
    
    def test_init_without_api_key(self):
        """Test that initialization without API key raises error."""
        with self.assertRaises(Exception):
            TranslatePlusClient(api_key="")
    
    def test_init_with_custom_base_url(self):
        """Test client initialization with custom base URL."""
        client = TranslatePlusClient(
            api_key="test-key",
            base_url="https://staging-api.translateplus.com"
        )
        self.assertEqual(client.base_url, "https://staging-api.translateplus.com")
        client.close()
    
    @patch('translateplus.client.requests.Session.request')
    def test_translate_success(self, mock_request):
        """Test successful translation."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "translations": {
                "text": "Hello",
                "translation": "Bonjour",
                "source": "en",
                "target": "fr"
            }
        }
        mock_request.return_value = mock_response
        
        result = self.client.translate("Hello", source="en", target="fr")
        
        self.assertEqual(result["translations"]["translation"], "Bonjour")
        mock_request.assert_called_once()
    
    @patch('translateplus.client.requests.Session.request')
    def test_translate_authentication_error(self, mock_request):
        """Test authentication error handling."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"detail": "Invalid API key"}
        mock_response.content = b'{"detail": "Invalid API key"}'
        mock_request.return_value = mock_response
        
        with self.assertRaises(TranslatePlusAuthenticationError):
            self.client.translate("Hello", source="en", target="fr")
    
    @patch('translateplus.client.requests.Session.request')
    def test_translate_rate_limit_error(self, mock_request):
        """Test rate limit error handling."""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.headers = {"Retry-After": "60"}
        mock_response.json.return_value = {"detail": "Rate limit exceeded"}
        mock_response.content = b'{"detail": "Rate limit exceeded"}'
        mock_request.return_value = mock_response
        
        with self.assertRaises(TranslatePlusRateLimitError):
            self.client.translate("Hello", source="en", target="fr")
    
    @patch('translateplus.client.requests.Session.request')
    def test_translate_insufficient_credits_error(self, mock_request):
        """Test insufficient credits error handling."""
        mock_response = Mock()
        mock_response.status_code = 402
        mock_response.json.return_value = {"detail": "Insufficient credits"}
        mock_response.content = b'{"detail": "Insufficient credits"}'
        mock_request.return_value = mock_response
        
        with self.assertRaises(TranslatePlusInsufficientCreditsError):
            self.client.translate("Hello", source="en", target="fr")
    
    def test_translate_batch_validation(self):
        """Test batch translation validation."""
        # Empty list
        with self.assertRaises(Exception):
            self.client.translate_batch([], source="en", target="fr")
        
        # Too many texts
        with self.assertRaises(Exception):
            self.client.translate_batch(["text"] * 101, source="en", target="fr")
    
    def test_translate_subtitles_validation(self):
        """Test subtitle translation validation."""
        # Invalid format
        with self.assertRaises(Exception):
            self.client.translate_subtitles("content", format="invalid", source="en", target="fr")
    
    def test_context_manager(self):
        """Test context manager protocol."""
        with TranslatePlusClient(api_key="test-key") as client:
            self.assertIsInstance(client, TranslatePlusClient)
        # Session should be closed after context exit


if __name__ == "__main__":
    unittest.main()
