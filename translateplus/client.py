"""Main TranslatePlus API client."""

import requests
from typing import Optional, Dict, List, Any, Union
from urllib.parse import urljoin
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Semaphore

from translateplus.exceptions import (
    TranslatePlusError,
    TranslatePlusAPIError,
    TranslatePlusAuthenticationError,
    TranslatePlusRateLimitError,
    TranslatePlusInsufficientCreditsError,
    TranslatePlusValidationError,
)


class TranslatePlusClient:
    """
    Official Python client for TranslatePlus API.
    
    This client provides a simple and intuitive interface to all TranslatePlus
    translation endpoints including text, batch, HTML, email, subtitles, and i18n translation.
    
    Example:
        >>> client = TranslatePlusClient(api_key="your-api-key")
        >>> result = client.translate(text="Hello", source="en", target="fr")
        >>> print(result["translations"]["translation"])
        'Bonjour'
    
    Args:
        api_key: Your TranslatePlus API key
        base_url: Base URL for the API (default: https://api.translateplus.io)
        timeout: Request timeout in seconds (default: 30)
        max_retries: Maximum number of retries for failed requests (default: 3)
        max_concurrent: Maximum number of concurrent requests (default: 5)
    """
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.translateplus.io",
        timeout: int = 30,
        max_retries: int = 3,
        max_concurrent: int = 5,
    ):
        if not api_key:
            raise TranslatePlusValidationError("API key is required")
        
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.max_concurrent = max_concurrent
        
        # Create session with default headers
        self.session = requests.Session()
        self.session.headers.update({
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"translateplus-python/1.0.0",
        })
        
        # Semaphore for concurrency control
        self._semaphore = Semaphore(max_concurrent)
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        files: Optional[Dict] = None,
        params: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Make an HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request body data
            files: Files to upload (for multipart/form-data)
            params: URL query parameters
            
        Returns:
            Response JSON as dictionary
            
        Raises:
            TranslatePlusAPIError: For API errors
            TranslatePlusAuthenticationError: For authentication errors
            TranslatePlusRateLimitError: For rate limit errors
            TranslatePlusInsufficientCreditsError: For insufficient credits
        """
        url = urljoin(self.base_url, endpoint.lstrip("/"))
        
        # Prepare headers
        headers = {}
        if files:
            # Remove Content-Type for multipart/form-data (requests will set it)
            headers = {}
        else:
            headers = {"Content-Type": "application/json"}
        
        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries + 1):
            try:
                with self._semaphore:  # Concurrency control
                    response = self.session.request(
                        method=method,
                        url=url,
                        json=data if not files else None,
                        data=data if files else None,
                        files=files,
                        params=params,
                        headers=headers,
                        timeout=self.timeout,
                    )
                    
                    # Handle rate limiting with exponential backoff
                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                        if attempt < self.max_retries:
                            time.sleep(retry_after)
                            continue
                        raise TranslatePlusRateLimitError(
                            "Rate limit exceeded. Please try again later.",
                            status_code=429,
                            response=response.json() if response.content else None,
                        )
                    
                    # Handle other errors
                    if response.status_code >= 400:
                        error_data = response.json() if response.content else {}
                        error_message = error_data.get("detail", f"API error: {response.status_code}")
                        
                        if response.status_code == 401 or response.status_code == 403:
                            raise TranslatePlusAuthenticationError(
                                error_message,
                                status_code=response.status_code,
                                response=error_data,
                            )
                        elif response.status_code == 402:
                            raise TranslatePlusInsufficientCreditsError(
                                error_message,
                                status_code=response.status_code,
                                response=error_data,
                            )
                        elif response.status_code == 429:
                            raise TranslatePlusRateLimitError(
                                error_message,
                                status_code=response.status_code,
                                response=error_data,
                            )
                        else:
                            raise TranslatePlusAPIError(
                                error_message,
                                status_code=response.status_code,
                                response=error_data,
                            )
                    
                    return response.json()
                    
            except (TranslatePlusAuthenticationError, TranslatePlusInsufficientCreditsError):
                # Don't retry authentication or credit errors
                raise
            except requests.exceptions.RequestException as e:
                last_exception = e
                if attempt < self.max_retries:
                    # Exponential backoff
                    time.sleep(2 ** attempt)
                    continue
                raise TranslatePlusAPIError(f"Request failed: {str(e)}")
        
        # If we get here, all retries failed
        raise TranslatePlusAPIError(
            f"Request failed after {self.max_retries} retries: {str(last_exception)}"
        )
    
    def translate(
        self,
        text: str,
        source: str = "auto",
        target: str = "en",
    ) -> Dict[str, Any]:
        """
        Translate a single text.
        
        Args:
            text: Text to translate (max 5000 characters)
            source: Source language code (e.g., 'en', 'fr', 'auto' for auto-detect)
            target: Target language code (e.g., 'en', 'fr')
            
        Returns:
            Translation result with text, translation, source, and target
            
        Example:
            >>> result = client.translate("Hello", source="en", target="fr")
            >>> print(result["translations"]["translation"])
            'Bonjour'
        """
        data = {
            "text": text,
            "source": source,
            "target": target,
        }
        return self._make_request("POST", "/v2/translate", data=data)
    
    def translate_batch(
        self,
        texts: List[str],
        source: str = "auto",
        target: str = "en",
    ) -> Dict[str, Any]:
        """
        Translate multiple texts in a single request.
        
        Args:
            texts: List of texts to translate (1-100 texts per request)
            source: Source language code (e.g., 'en', 'fr', 'auto' for auto-detect)
            target: Target language code (e.g., 'en', 'fr')
            
        Returns:
            Batch translation result with translations array
            
        Example:
            >>> texts = ["Hello", "How are you?"]
            >>> result = client.translate_batch(texts, source="en", target="fr")
            >>> for translation in result["translations"]:
            ...     print(translation["translation"])
            'Bonjour'
            'Comment allez-vous ?'
        """
        if not texts or len(texts) == 0:
            raise TranslatePlusValidationError("Texts list cannot be empty")
        if len(texts) > 100:
            raise TranslatePlusValidationError("Maximum 100 texts allowed per batch request")
        
        data = {
            "texts": texts,
            "source": source,
            "target": target,
        }
        return self._make_request("POST", "/v2/translate/batch", data=data)
    
    def translate_html(
        self,
        html: str,
        source: str = "auto",
        target: str = "en",
    ) -> Dict[str, Any]:
        """
        Translate HTML content while preserving all tags and structure.
        
        Args:
            html: HTML content to translate
            source: Source language code (e.g., 'en', 'fr', 'auto' for auto-detect)
            target: Target language code (e.g., 'en', 'fr')
            
        Returns:
            Translated HTML content
            
        Example:
            >>> html = "<p>Hello <b>world</b></p>"
            >>> result = client.translate_html(html, source="en", target="fr")
            >>> print(result["html"])
            '<p>Bonjour <b>monde</b></p>'
        """
        data = {
            "html": html,
            "source": source,
            "target": target,
        }
        return self._make_request("POST", "/v2/translate/html", data=data)
    
    def translate_email(
        self,
        subject: str,
        email_body: str,
        source: str = "auto",
        target: str = "en",
    ) -> Dict[str, Any]:
        """
        Translate email subject and HTML body.
        
        Args:
            subject: Email subject to translate
            email_body: Email HTML body to translate
            source: Source language code (e.g., 'en', 'fr', 'auto' for auto-detect)
            target: Target language code (e.g., 'en', 'fr')
            
        Returns:
            Translated email with subject and html_body
            
        Example:
            >>> result = client.translate_email(
            ...     subject="Welcome",
            ...     email_body="<p>Thank you for signing up!</p>",
            ...     source="en",
            ...     target="fr"
            ... )
            >>> print(result["subject"])
            'Bienvenue'
        """
        data = {
            "subject": subject,
            "email_body": email_body,
            "source": source,
            "target": target,
        }
        return self._make_request("POST", "/v2/translate/email", data=data)
    
    def translate_subtitles(
        self,
        content: str,
        format: str = "srt",
        source: str = "auto",
        target: str = "en",
    ) -> Dict[str, Any]:
        """
        Translate subtitle files (SRT or VTT format).
        
        Args:
            content: Subtitle file content
            format: Subtitle format ('srt' or 'vtt')
            source: Source language code (e.g., 'en', 'fr', 'auto' for auto-detect)
            target: Target language code (e.g., 'en', 'fr')
            
        Returns:
            Translated subtitle content
            
        Example:
            >>> srt_content = "1\\n00:00:01,000 --> 00:00:02,000\\nHello world\\n"
            >>> result = client.translate_subtitles(srt_content, format="srt", source="en", target="fr")
            >>> print(result["content"])
            '1\\n00:00:01,000 --> 00:00:02,000\\nBonjour le monde\\n'
        """
        if format not in ["srt", "vtt"]:
            raise TranslatePlusValidationError("Format must be 'srt' or 'vtt'")
        
        data = {
            "content": content,
            "format": format,
            "source": source,
            "target": target,
        }
        return self._make_request("POST", "/v2/translate/subtitles", data=data)
    
    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect the language of a text.
        
        Args:
            text: Text to detect language from (max 5000 characters)
            
        Returns:
            Language detection result with detected language code and confidence
            
        Example:
            >>> result = client.detect_language("Bonjour le monde")
            >>> print(result["language_detection"]["language"])
            'fr'
        """
        data = {"text": text}
        return self._make_request("POST", "/v2/language/detect", data=data)
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """
        Get list of supported languages.
        
        Returns:
            Dictionary with supported languages
            
        Example:
            >>> languages = client.get_supported_languages()
            >>> print(languages["languages"]["en"])
            'English'
        """
        return self._make_request("GET", "/v2/language/supported")
    
    def get_account_summary(self) -> Dict[str, Any]:
        """
        Get account summary including credits, plan, and usage.
        
        Returns:
            Account summary with credits, plan, and usage information
            
        Example:
            >>> summary = client.get_account_summary()
            >>> print(f"Credits remaining: {summary['credits_remaining']}")
            'Credits remaining: 1000'
        """
        return self._make_request("GET", "/v2/user/account")
    
    def create_i18n_job(
        self,
        file_path: str,
        target_languages: List[str],
        source_language: str = "auto",
        webhook_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Create an i18n translation job.
        
        Args:
            file_path: Path to the i18n file (JSON, YAML, PO, etc.)
            target_languages: List of target language codes (e.g., ['fr', 'es', 'de'])
            source_language: Source language code (default: 'auto' for auto-detect)
            webhook_url: Optional webhook URL to receive notification when job completes
            
        Returns:
            Job creation result with job ID and status
            
        Example:
            >>> result = client.create_i18n_job(
            ...     file_path="locales/en.json",
            ...     target_languages=["fr", "es"],
            ...     source_language="en"
            ... )
            >>> print(f"Job ID: {result['job_id']}")
            'Job ID: 12345'
        """
        with open(file_path, "rb") as f:
            files = {"file": f}
            data = {
                "source_language": source_language,
                "target_languages": ",".join(target_languages),
            }
            if webhook_url:
                data["webhook_url"] = webhook_url
            
            return self._make_request("POST", "/v2/i18n/jobs", data=data, files=files)
    
    def get_i18n_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get the status of an i18n translation job.
        
        Args:
            job_id: Job ID returned from create_i18n_job
            
        Returns:
            Job status information
            
        Example:
            >>> status = client.get_i18n_job_status("12345")
            >>> print(status["status"])
            'completed'
        """
        return self._make_request("GET", f"/v2/i18n/jobs/{job_id}")
    
    def list_i18n_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        List all i18n translation jobs.
        
        Args:
            page: Page number (default: 1)
            page_size: Number of jobs per page (default: 20)
            
        Returns:
            List of jobs with pagination information
            
        Example:
            >>> jobs = client.list_i18n_jobs(page=1, page_size=10)
            >>> for job in jobs["results"]:
            ...     print(f"Job {job['id']}: {job['status']}")
        """
        params = {"page": page, "page_size": page_size}
        return self._make_request("GET", "/v2/i18n/jobs", params=params)
    
    def download_i18n_file(self, job_id: str, language_code: str) -> bytes:
        """
        Download a translated i18n file.
        
        Args:
            job_id: Job ID
            language_code: Target language code (e.g., 'fr', 'es')
            
        Returns:
            File content as bytes
            
        Example:
            >>> content = client.download_i18n_file("12345", "fr")
            >>> with open("locales/fr.json", "wb") as f:
            ...     f.write(content)
        """
        url = urljoin(self.base_url, f"/v2/i18n/jobs/{job_id}/download/{language_code}")
        response = self.session.get(
            url,
            headers={"X-API-KEY": self.api_key},
            timeout=self.timeout,
        )
        
        if response.status_code >= 400:
            error_data = response.json() if response.content else {}
            error_message = error_data.get("detail", f"API error: {response.status_code}")
            raise TranslatePlusAPIError(
                error_message,
                status_code=response.status_code,
                response=error_data,
            )
        
        return response.content
    
    def delete_i18n_job(self, job_id: str) -> Dict[str, Any]:
        """
        Delete an i18n translation job.
        
        Args:
            job_id: Job ID to delete
            
        Returns:
            Deletion confirmation
            
        Example:
            >>> client.delete_i18n_job("12345")
        """
        return self._make_request("DELETE", f"/v2/i18n/jobs/{job_id}")
    
    def translate_concurrent(
        self,
        texts: List[str],
        source: str = "auto",
        target: str = "en",
        max_workers: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Translate multiple texts concurrently using parallel requests.
        
        This method uses ThreadPoolExecutor to send multiple translation requests
        in parallel, respecting the client's max_concurrent setting.
        
        Args:
            texts: List of texts to translate
            source: Source language code
            target: Target language code
            max_workers: Maximum number of worker threads (default: max_concurrent)
            
        Returns:
            List of translation results in the same order as input texts
            
        Example:
            >>> texts = ["Hello", "Goodbye", "Thank you"]
            >>> results = client.translate_concurrent(texts, source="en", target="fr")
            >>> for result in results:
            ...     print(result["translations"]["translation"])
            'Bonjour'
            'Au revoir'
            'Merci'
        """
        if max_workers is None:
            max_workers = self.max_concurrent
        
        results = [None] * len(texts)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(self.translate, text, source, target): i
                for i, text in enumerate(texts)
            }
            
            for future in as_completed(future_to_index):
                index = future_to_index[future]
                try:
                    results[index] = future.result()
                except Exception as e:
                    results[index] = {"error": str(e)}
        
        return results
    
    def close(self):
        """Close the HTTP session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
