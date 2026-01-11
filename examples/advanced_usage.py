"""Advanced usage examples for TranslatePlus Python client."""

from translateplus import TranslatePlusClient

# Initialize client with custom settings
client = TranslatePlusClient(
    api_key="your-api-key-here",
    max_concurrent=10,  # Allow up to 10 concurrent requests
    max_retries=5,  # Retry up to 5 times
    timeout=60,  # 60 second timeout
)

# Example 1: Concurrent translation
print("=== Example 1: Concurrent Translation ===")
texts = [
    "Hello",
    "Goodbye",
    "Thank you",
    "Please",
    "Sorry",
    "Yes",
    "No",
    "Maybe",
]

results = client.translate_concurrent(
    texts=texts,
    source="en",
    target="fr",
    max_workers=5
)

for i, result in enumerate(results):
    if "error" not in result:
        print(f"{texts[i]} -> {result['translations']['translation']}")
    else:
        print(f"{texts[i]} -> Error: {result['error']}")
print()

# Example 2: Translate email
print("=== Example 2: Email Translation ===")
result = client.translate_email(
    subject="Welcome to our service",
    email_body="<p>Thank you for signing up!</p><p>We're excited to have you.</p>",
    source="en",
    target="fr"
)
print(f"Subject: {result['subject']}")
print(f"Body: {result['html_body']}")
print()

# Example 3: Translate subtitles
print("=== Example 3: Subtitle Translation ===")
srt_content = """1
00:00:01,000 --> 00:00:02,000
Hello world

2
00:00:03,000 --> 00:00:04,000
How are you?
"""

result = client.translate_subtitles(
    content=srt_content,
    format="srt",
    source="en",
    target="fr"
)
print("Translated subtitles:")
print(result["content"])
print()

# Example 4: Using context manager
print("=== Example 4: Context Manager ===")
with TranslatePlusClient(api_key="your-api-key-here") as client:
    result = client.translate("Hello", source="en", target="fr")
    print(f"Translation: {result['translations']['translation']}")
# Session automatically closed
print()

# Example 5: Error handling
print("=== Example 5: Error Handling ===")
from translateplus.exceptions import (
    TranslatePlusAuthenticationError,
    TranslatePlusInsufficientCreditsError,
    TranslatePlusRateLimitError,
)

try:
    result = client.translate("Hello", source="en", target="fr")
except TranslatePlusAuthenticationError:
    print("Authentication failed - check your API key")
except TranslatePlusInsufficientCreditsError:
    print("Insufficient credits - please upgrade your plan")
except TranslatePlusRateLimitError:
    print("Rate limit exceeded - please wait and try again")
except Exception as e:
    print(f"Unexpected error: {e}")
