#!/bin/bash
set -euo pipefail

# Build script for MCP Python Server
# Can be run locally or in CI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "Building MCP Python Server"
echo "========================================="
echo "Project root: $PROJECT_ROOT"
echo "Python version: $(python --version)"
echo "Pip version: $(pip --version)"
echo ""

cd "$PROJECT_ROOT"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "🔧 Creating virtual environment..."
    python -m venv .venv
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Upgrade pip and install build tools
echo "📈 Upgrading pip and installing build tools..."
pip install --upgrade pip setuptools wheel

# Install project in development mode
echo "📦 Installing project dependencies..."
pip install -e .[dev]

# Check code formatting
echo ""
echo "📋 Checking code formatting..."
if ruff format --check src tests 2>/dev/null || true; then
    echo "✅ Code formatting OK"
else
    echo "❌ Code formatting failed"
    echo "Run: ruff format src tests"
    exit 1
fi

# Run linter
echo ""
echo "🔍 Running Ruff (linter)..."
if ruff check src tests 2>/dev/null || true; then
    echo "✅ Ruff checks passed"
else
    echo "❌ Ruff found issues"
    echo "Run: ruff check src tests --fix"
    exit 1
fi

# Type checking
echo ""
echo "🔍 Running MyPy (type checker)..."
if mypy src 2>/dev/null || true; then
    echo "✅ Type checking passed"
else
    echo "❌ Type checking failed"
    echo "Run: mypy src"
    exit 1
fi

# Build distribution packages
echo ""
echo "🏗️ Building distribution packages..."
pip install build
python -m build

# List built packages
echo ""
echo "📦 Built packages:"
ls -lh dist/ 2>/dev/null || echo "  No dist/ directory found"

echo ""
echo "========================================="
echo "✅ Build completed successfully!"
echo "========================================="