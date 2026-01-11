"""Basic usage examples for TranslatePlus Python client."""

from translateplus import TranslatePlusClient

# Initialize client
client = TranslatePlusClient(api_key="your-api-key-here")

# Example 1: Translate a single text
print("=== Example 1: Single Translation ===")
result = client.translate(
    text="Hello, world!",
    source="en",
    target="fr"
)
print(f"Original: Hello, world!")
print(f"Translated: {result['translations']['translation']}")
print()

# Example 2: Batch translation
print("=== Example 2: Batch Translation ===")
texts = ["Hello", "Goodbye", "Thank you"]
result = client.translate_batch(texts, source="en", target="fr")
for translation in result["translations"]:
    if translation["success"]:
        print(f"{translation['text']} -> {translation['translation']}")
print()

# Example 3: HTML translation
print("=== Example 3: HTML Translation ===")
html = "<p>Hello <b>world</b></p>"
result = client.translate_html(html, source="en", target="fr")
print(f"Original: {html}")
print(f"Translated: {result['html']}")
print()

# Example 4: Language detection
print("=== Example 4: Language Detection ===")
result = client.detect_language("Bonjour le monde")
print(f"Detected language: {result['language_detection']['language']}")
print(f"Confidence: {result['language_detection']['confidence']}")
print()

# Example 5: Get supported languages
print("=== Example 5: Supported Languages ===")
languages = client.get_supported_languages()
print(f"Total languages: {len(languages['languages'])}")
print("Sample languages:")
for code, name in list(languages["languages"].items())[:5]:
    print(f"  {code}: {name}")
print()

# Example 6: Account summary
print("=== Example 6: Account Summary ===")
summary = client.get_account_summary()
print(f"Credits remaining: {summary.get('credits_remaining', 'N/A')}")
print(f"Current plan: {summary.get('plan_name', 'N/A')}")
print()

# Close the client
client.close()
