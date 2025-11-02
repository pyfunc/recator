#!/bin/bash
# Recator Installation Script

echo "╔═══════════════════════════════════════════╗"
echo "║     RECATOR - Installation Script          ║"
echo "╚═══════════════════════════════════════════╝"
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '(?<=Python )\d+\.\d+')
required_version="3.7"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Error: Python 3.7+ is required (found $python_version)"
    exit 1
fi

echo "✅ Python version: $python_version"

# Install the package
echo "📦 Installing Recator library..."

if pip install -e . ; then
    echo "✅ Recator installed successfully!"
    echo ""
    echo "🚀 You can now use Recator:"
    echo "   • Command line: recator /path/to/project"
    echo "   • Python: from recator import Recator"
    echo ""
    echo "📖 Run 'recator --help' for usage information"
else
    echo "❌ Installation failed"
    exit 1
fi

# Optional: Run test
read -p "Would you like to run a quick test? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🧪 Running test..."
    python3 test_example.py
fi

echo ""
echo "✨ Installation complete!"
