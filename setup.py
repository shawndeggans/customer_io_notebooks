"""Setup script for Customer.IO API client library."""

from setuptools import setup, find_packages

setup(
    name="customerio-api-client",
    version="1.0.0",
    description="Complete Python client library for Customer.IO APIs with notebook compatibility bridge modules",
    author="Customer.IO Integration Team",
    author_email="support@example.com",
    packages=find_packages(where="src") + ["utils", "app_utils", "webhook_utils"],
    package_dir={"": "src", "utils": "utils", "app_utils": "app_utils", "webhook_utils": "webhook_utils"},
    python_requires=">=3.11",
    install_requires=[
        "requests>=2.28.0",
        "python-dotenv>=0.19.0",
        "typing-extensions>=4.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ],
        "notebooks": [
            "jupyter>=1.0.0",
            "jupyterlab>=4.0.0",
            "ipython>=8.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Communications :: Email",
    ],
    project_urls={
        "Documentation": "https://github.com/your-org/customerio-api-client",
        "Source": "https://github.com/your-org/customerio-api-client",
        "Tracker": "https://github.com/your-org/customerio-api-client/issues",
    },
)