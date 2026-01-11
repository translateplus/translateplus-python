"""Setup script for translateplus package."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="translateplus-python",
    version="2.0.5",
    author="TranslatePlus",
    author_email="support@translateplus.io",
    description="Official Python client library for TranslatePlus API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/translateplus/translateplus-python",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
    ],
    extras_require={
        "async": [
            "aiohttp>=3.9.0",
            "asyncio-throttle>=1.0.0",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
