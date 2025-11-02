# Recator 🔧

**Recator** - Automated code duplicate detection and refactoring library for Python

[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

## 📋 Overview

Recator is a powerful Python library that automatically detects and refactors code duplicates across multiple programming languages using simple heuristics without requiring LLMs. It works efficiently on CPU and supports various programming languages including Python, JavaScript, Java, C/C++, and more.

## ✨ Features

- **Multi-language Support**: Python, JavaScript, Java, C/C++, C#, PHP, Ruby, Go, Rust, Kotlin, Swift
- **Multiple Detection Algorithms**:
  - Exact duplicate detection (hash-based)
  - Token-based similarity detection
  - Fuzzy matching using sequence comparison
  - Structural similarity detection (same structure, different names)
- **Automated Refactoring Strategies**:
  - Extract Method - for duplicate code blocks
  - Extract Class - for structural duplicates
  - Extract Module - for file-level duplicates
  - Parameterize - for similar code with differences
- **Safe Mode**: Creates `.refactored` versions without modifying originals
- **CPU Efficient**: Uses simple heuristics, no GPU or LLM required
- **Configurable**: Adjustable thresholds and parameters

## 🚀 Installation

```bash
# Basic installation
pip install recator

# Or install from source
git clone https://github.com/yourusername/recator.git
cd recator
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install with advanced features
pip install -e ".[advanced]"
```

## 📖 Usage

### Command Line Interface

```bash
# Basic analysis
recator /path/to/project

# Verbose analysis with custom parameters
recator /path/to/project -v --min-lines 6 --threshold 0.9

# Preview refactoring suggestions
recator /path/to/project --refactor

# Apply refactoring (creates .refactored files)
recator /path/to/project --refactor --apply

# Analyze specific languages only
recator /path/to/project --languages python javascript

# Exclude patterns
recator /path/to/project --exclude "*.test.js" "build/*"

# Save results to JSON
recator /path/to/project --output results.json
```

### Python API

```python
from recator import Recator

# Initialize with project path
recator = Recator('/path/to/project')

# Analyze for duplicates
results = recator.analyze()
print(f"Found {results['duplicates_found']} duplicates")

# Get detailed duplicate information
for duplicate in results['duplicates']:
    print(f"Type: {duplicate['type']}")
    print(f"Files: {duplicate.get('files', [])}")
    print(f"Confidence: {duplicate.get('confidence', 0)}")

# Preview refactoring
preview = recator.refactor_duplicates(dry_run=True)
print(f"Estimated LOC reduction: {preview['estimated_loc_reduction']}")

# Apply refactoring
refactoring_results = recator.refactor_duplicates(dry_run=False)
print(f"Modified {len(refactoring_results['modified_files'])} files")
```

### Custom Configuration

```python
from recator import Recator

config = {
    'min_lines': 5,                    # Minimum lines for duplicate
    'min_tokens': 40,                  # Minimum tokens for duplicate
    'similarity_threshold': 0.90,      # Similarity threshold (0-1)
    'languages': ['python', 'java'],   # Languages to analyze
    'exclude_patterns': ['*.min.js'],  # Patterns to exclude
    'safe_mode': True,                 # Don't modify originals
}

recator = Recator('/path/to/project', config)
results = recator.analyze()
```

## 🔍 Detection Algorithms

### 1. Exact Duplicate Detection
Finds identical code blocks using hash comparison.

### 2. Token-based Detection
Compares token sequences to find duplicates that may have different formatting.

### 3. Fuzzy Matching
Uses sequence matching algorithms to find similar (but not identical) code.

### 4. Structural Detection
Identifies code with the same structure but different variable/function names.

## 🛠️ Refactoring Strategies

### Extract Method
```python
# Before: Duplicate blocks in multiple places
def process_user(user):
    # validation block (duplicate)
    if not user.email:
        raise ValueError("Email required")
    if "@" not in user.email:
        raise ValueError("Invalid email")
    # ... processing

def update_user(user):
    # validation block (duplicate)
    if not user.email:
        raise ValueError("Email required")
    if "@" not in user.email:
        raise ValueError("Invalid email")
    # ... updating

# After: Extracted method
def validate_user_email(user):
    if not user.email:
        raise ValueError("Email required")
    if "@" not in user.email:
        raise ValueError("Invalid email")

def process_user(user):
    validate_user_email(user)
    # ... processing

def update_user(user):
    validate_user_email(user)
    # ... updating
```

### Extract Module
Creates shared modules for file-level duplicates.

### Parameterize
Converts similar code with differences into parameterized functions.

## 📊 Example Output

```
╔═══════════════════════════════════════════╗
║        RECATOR - Code Refactoring Bot     ║
║     Eliminate Code Duplicates with Ease   ║
╚═══════════════════════════════════════════╝

🔍 Initializing Recator for: /home/user/project
🔎 Analyzing project for duplicates...

📊 Analysis Results:
  • Total files scanned: 45
  • Files parsed: 42
  • Duplicates found: 8

📋 Duplicate Details:
  [1] Type: exact_block
      Files: utils.py, helpers.py, validation.py
      Confidence: 100%
      Lines: 12

  [2] Type: fuzzy
      Files: api_client.py, http_handler.py
      Confidence: 87%
      Lines: 25

🔧 Refactoring Preview:
  • Total actions: 8
  • Estimated LOC reduction: 147
  • Affected files: 12

✅ Done!
```

## 🔧 Configuration File

Create a `recator.json` configuration file:

```json
{
  "min_lines": 4,
  "min_tokens": 30,
  "similarity_threshold": 0.85,
  "languages": ["python", "javascript", "java"],
  "exclude_patterns": [
    "*.min.js",
    "*.min.css",
    "node_modules/*",
    ".git/*",
    "build/*",
    "dist/*"
  ],
  "safe_mode": true
}
```

Use with: `recator /path/to/project --config recator.json`

## 🏗️ Architecture

```
recator/
├── __init__.py       # Main Recator class
├── scanner.py        # File scanning and reading
├── analyzer.py       # Code parsing and tokenization
├── detector.py       # Duplicate detection algorithms
├── refactor.py       # Refactoring strategies
└── cli.py           # Command-line interface
```

## 📝 Supported Languages

- **Python** (.py)
- **JavaScript/TypeScript** (.js, .jsx, .ts, .tsx)
- **Java** (.java)
- **C/C++** (.c, .cpp, .cc, .cxx, .h, .hpp)
- **C#** (.cs)
- **PHP** (.php)
- **Ruby** (.rb)
- **Go** (.go)
- **Rust** (.rs)
- **Kotlin** (.kt)
- **Swift** (.swift)

## ⚙️ How It Works

1. **Scanning**: Traverses project directory to find source files
2. **Parsing**: Tokenizes and parses code into analyzable structures
3. **Detection**: Applies multiple algorithms to find duplicates
4. **Analysis**: Groups and ranks duplicates by confidence
5. **Refactoring**: Suggests or applies appropriate refactoring strategies
6. **Output**: Generates modified files or preview reports

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under theApacheLicense.

## 🙏 Acknowledgments

Built using only Python standard library for maximum compatibility and efficiency.

## 📮 Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ for cleaner, more maintainable code
