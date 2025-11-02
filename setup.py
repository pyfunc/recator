"""
Setup script for Recator - Code Duplicate Detection and Refactoring Library
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

setup(
    name="recator",
    version="0.1.0",
    author="Recator Team",
    author_email="recator@example.com",
    description="Automated code duplicate detection and refactoring library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pyfunc/recator",
    packages=["recator"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        # No external dependencies for basic functionality
        # Using only Python standard library
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.9",
            "build>=1.0.0",
            "twine>=4.0.0",
        ],
        "advanced": [
            "tree-sitter>=0.20",  # For better AST parsing
            "pygments>=2.10",     # For syntax highlighting
            "click>=8.0",         # For better CLI
        ]
    },
    entry_points={
        "console_scripts": [
            "recator=recator.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
