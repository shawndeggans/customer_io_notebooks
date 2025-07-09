"""Setup configuration for Customer.IO API Client Library.

This setup.py packages the Customer.IO API client modules for distribution
and installation on Databricks clusters.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [
        line.strip() 
        for line in fh 
        if line.strip() and not line.startswith("#") and not line.startswith("pytest")
    ]

setup(
    name="customerio-api-client",
    version="1.0.0",
    author="Customer.IO Integration Team",
    description="Customer.IO API Client Library for Data Pipelines, App API, and Webhooks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/customer_io_notebooks",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.11.1",
            "mypy>=1.8.0",
            "ruff>=0.1.9",
            "faker>=24.0.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "jupyterlab>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            # Add any command-line tools here if needed
        ],
    },
)