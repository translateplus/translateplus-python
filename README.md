# TranslatePlus Python Client

[![PyPI version](https://badge.fury.io/py/translateplus.svg)](https://badge.fury.io/py/translateplus)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official Python client library for [TranslatePlus API](https://translateplus.io) - Professional translation service for text, HTML, emails, subtitles, and i18n files in 100+ languages.

## Features

- ✅ **Simple & Intuitive API** - Easy to use, Pythonic interface
- ✅ **All Endpoints Supported** - Text, batch, HTML, email, subtitles, and i18n translation
- ✅ **Concurrent Requests** - Built-in support for parallel translations
- ✅ **Error Handling** - Comprehensive exception handling with detailed error messages
- ✅ **Type Hints** - Full type annotations for better IDE support
- ✅ **Production Ready** - Retry logic, rate limiting, and connection pooling
- ✅ **100+ Languages** - Support for all languages available in TranslatePlus

## Installation

```bash
pip install translateplus
```

For async support (optional):

```bash
pip install translateplus[async]
```

## Quick Start

```python
from translateplus import TranslatePlusClient

# Initialize client
client = TranslatePlusClient(api_key="your-api-key")

# Translate a single text
result = client.translate(
    text="Hello, world!",
    source="en",
    target="fr"
)
print(result["translations"]["translation"])
# Output: "Bonjour le monde !"

# Translate multiple texts
texts = ["Hello", "Goodbye", "Thank you"]
result = client.translate_batch(texts, source="en", target="fr")
for translation in result["translations"]:
    print(translation["translation"])

# Translate HTML
html = "<p>Hello <b>world</b></p>"
result = client.translate_html(html, source="en", target="fr")
print(result["html"])
# Output: "<p>Bonjour <b>monde</b></p>"
```

## Documentation

### Authentication

```python
from translateplus import TranslatePlusClient

client = TranslatePlusClient(
    api_key="your-api-key",
    base_url="https://api.translateplus.io",  # Optional, defaults to production
    timeout=30,  # Request timeout in seconds
    max_retries=3,  # Maximum retries for failed requests
    max_concurrent=5,  # Maximum concurrent requests
)
```

### Text Translation

#### Single Translation

```python
result = client.translate(
    text="My client speaks only French. Will you translate for me?",
    source="en",
    target="fr"
)

print(result["translations"]["translation"])
print(result["translations"]["source"])  # Detected source language
print(result["translations"]["target"])  # Target language
```

#### Batch Translation

```python
texts = [
    "Hello, how are you?",
    "What is your name?",
    "Thank you very much!"
]

result = client.translate_batch(
    texts=texts,
    source="en",
    target="fr"
)

print(f"Total: {result['total']}")
print(f"Successful: {result['successful']}")
print(f"Failed: {result['failed']}")

for translation in result["translations"]:
    if translation["success"]:
        print(f"{translation['text']} -> {translation['translation']}")
    else:
        print(f"Error: {translation.get('error', 'Unknown error')}")
```

#### Concurrent Translation

For better performance when translating many texts:

```python
texts = ["Hello", "Goodbye", "Thank you", "Please", "Sorry"]

# Translate all texts concurrently
results = client.translate_concurrent(
    texts=texts,
    source="en",
    target="fr",
    max_workers=5  # Optional, defaults to max_concurrent
)

for result in results:
    if "error" not in result:
        print(result["translations"]["translation"])
```

### HTML Translation

```python
html_content = """
<html>
    <body>
        <h1>Welcome</h1>
        <p>This is a <strong>test</strong> paragraph.</p>
    </body>
</html>
"""

result = client.translate_html(
    html=html_content,
    source="en",
    target="fr"
)

print(result["html"])
# HTML structure is preserved, only text content is translated
```

### Email Translation

```python
result = client.translate_email(
    subject="Welcome to our service",
    email_body="<p>Thank you for signing up!</p><p>We're excited to have you.</p>",
    source="en",
    target="fr"
)

print(result["subject"])  # Translated subject
print(result["html_body"])  # Translated HTML body
```

### Subtitle Translation

```python
srt_content = """1
00:00:01,000 --> 00:00:02,000
Hello world

2
00:00:03,000 --> 00:00:04,000
How are you?
"""

result = client.translate_subtitles(
    content=srt_content,
    format="srt",  # or "vtt"
    source="en",
    target="fr"
)

print(result["content"])
# Timestamps are preserved, only text is translated
```

### Language Detection

```python
result = client.detect_language("Bonjour le monde")
print(result["language_detection"]["language"])  # "fr"
print(result["language_detection"]["confidence"])  # 0.99
```

### Supported Languages

```python
languages = client.get_supported_languages()
for code, name in languages["languages"].items():
    print(f"{code}: {name}")
```

### Account Information

```python
summary = client.get_account_summary()
print(f"Credits remaining: {summary['credits_remaining']}")
print(f"Current plan: {summary['plan_name']}")
print(f"Concurrency limit: {summary['concurrency_limit']}")
```

### i18n Translation Jobs

#### Create Job

```python
result = client.create_i18n_job(
    file_path="locales/en.json",
    target_languages=["fr", "es", "de"],
    source_language="en",
    webhook_url="https://your-app.com/webhook"  # Optional
)

job_id = result["job_id"]
print(f"Job created: {job_id}")
```

#### Check Job Status

```python
status = client.get_i18n_job_status(job_id)
print(f"Status: {status['status']}")  # pending, processing, completed, failed
print(f"Progress: {status.get('progress', 0)}%")
```

#### List Jobs

```python
jobs = client.list_i18n_jobs(page=1, page_size=20)
for job in jobs["results"]:
    print(f"Job {job['id']}: {job['status']}")
```

#### Download Translated File

```python
# Download French translation
content = client.download_i18n_file(job_id, "fr")
with open("locales/fr.json", "wb") as f:
    f.write(content)
```

#### Delete Job

```python
client.delete_i18n_job(job_id)
```

## Error Handling

The library provides specific exception types for different error scenarios:

```python
from translateplus import (
    TranslatePlusClient,
    TranslatePlusError,
    TranslatePlusAPIError,
    TranslatePlusAuthenticationError,
    TranslatePlusRateLimitError,
    TranslatePlusInsufficientCreditsError,
    TranslatePlusValidationError,
)

client = TranslatePlusClient(api_key="your-api-key")

try:
    result = client.translate("Hello", source="en", target="fr")
except TranslatePlusAuthenticationError:
    print("Invalid API key")
except TranslatePlusInsufficientCreditsError:
    print("Insufficient credits")
except TranslatePlusRateLimitError:
    print("Rate limit exceeded")
except TranslatePlusAPIError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.status_code}")
except TranslatePlusError as e:
    print(f"Error: {e}")
```

## Context Manager

The client supports Python's context manager protocol:

```python
with TranslatePlusClient(api_key="your-api-key") as client:
    result = client.translate("Hello", source="en", target="fr")
    print(result["translations"]["translation"])
# Session is automatically closed
```

## Advanced Usage

### Custom Base URL

For testing or using a different environment:

```python
client = TranslatePlusClient(
    api_key="your-api-key",
    base_url="https://staging-api.translateplus.io"
)
```

### Adjusting Concurrency

```python
# Allow up to 10 concurrent requests
client = TranslatePlusClient(
    api_key="your-api-key",
    max_concurrent=10
)
```

### Retry Configuration

```python
# Retry up to 5 times for failed requests
client = TranslatePlusClient(
    api_key="your-api-key",
    max_retries=5
)
```

## Examples

### Translate a List of Documents

```python
documents = [
    "Document 1 content...",
    "Document 2 content...",
    "Document 3 content...",
]

results = client.translate_concurrent(
    documents,
    source="en",
    target="fr"
)

for i, result in enumerate(results):
    if "error" not in result:
        print(f"Document {i+1}: {result['translations']['translation']}")
```

### Translate HTML Email Template

```python
email_template = """
<html>
    <body>
        <h1>Welcome {{name}}!</h1>
        <p>Thank you for joining us.</p>
    </body>
</html>
"""

# Translate to multiple languages
languages = ["fr", "es", "de"]
translations = {}

for lang in languages:
    result = client.translate_html(email_template, source="en", target=lang)
    translations[lang] = result["html"]
```

### Batch Process Subtitles

```python
import os

subtitle_files = ["subtitle1.srt", "subtitle2.srt", "subtitle3.srt"]

for file_path in subtitle_files:
    with open(file_path, "r") as f:
        content = f.read()
    
    result = client.translate_subtitles(
        content=content,
        format="srt",
        source="en",
        target="fr"
    )
    
    # Save translated subtitle
    output_path = file_path.replace(".srt", "_fr.srt")
    with open(output_path, "w") as f:
        f.write(result["content"])
```

## Requirements

- Python 3.8+
- requests >= 2.31.0

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://docs.translateplus.io](https://docs.translateplus.io)
- **API Reference**: [https://docs.translateplus.io/reference/v2/translation/translate](https://docs.translateplus.io/reference/v2/translation/translate)
- **Issues**: [GitHub Issues](https://github.com/translateplus/translateplus-python/issues)
- **Email**: support@translateplus.io

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Changelog

### 2.0.0 (2024-01-12)

- Initial release
- Support for all TranslatePlus API endpoints
- Concurrent translation support
- Comprehensive error handling
- Full type hints
