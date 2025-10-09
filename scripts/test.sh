#!/bin/bash
set -euo pipefail

# Test script for MCP Python Server
# Can be run locally or in CI

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "Testing MCP Python Server"
echo "========================================="
echo "Project root: $PROJECT_ROOT"
echo ""

cd "$PROJECT_ROOT"

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo "📦 Activating virtual environment..."
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source .venv/Scripts/activate
    else
        source .venv/bin/activate
    fi
fi

# Install test dependencies if not already installed
echo "📦 Ensuring test dependencies are installed..."
pip install -e .[dev] >/dev/null 2>&1 || true

# Create test directory if it doesn't exist
if [ ! -d "tests" ]; then
    echo "📁 Creating tests directory..."
    mkdir -p tests
    
    # Create a basic test file
    cat > tests/test_basic.py << 'EOF'
"""Basic tests for MCP Python Example."""

def test_imports():
    """Test that main modules can be imported."""
    from mcp_python_example import auth
    from mcp_python_example.bin import mcp_server, launcher, token_manager, mcp_client
    
    assert auth is not None
    assert mcp_server is not None
    assert launcher is not None  
    assert token_manager is not None
    assert mcp_client is not None


def test_auth_config():
    """Test auth configuration creation."""
    from mcp_python_example.auth import TokenClaims
    
    # Test TokenClaims model
    claims = TokenClaims(
        sub="testuser",
        iat=1234567890,
        exp=9999999999,
        iss="test"
    )
    
    assert claims.sub == "testuser"
    assert claims.iat == 1234567890
    assert claims.exp == 9999999999
    assert claims.iss == "test"
EOF
fi

# Run tests
echo "🧪 Running tests..."
if pytest tests/ -v --tb=short; then
    echo "✅ All tests passed"
else
    echo "❌ Some tests failed"
    exit 1
fi

# Test CLI tools (basic smoke tests)
echo ""
echo "🧪 Testing CLI tools..."

# Test token manager help
echo "Testing token-manager help..."
if python -m mcp_python_example.bin.token_manager --help >/dev/null 2>&1; then
    echo "✅ token-manager CLI works"
else
    echo "❌ token-manager CLI failed"
    exit 1
fi

# Test launcher help  
echo "Testing launcher help..."
if python -m mcp_python_example.bin.launcher --help >/dev/null 2>&1; then
    echo "✅ launcher CLI works"
else
    echo "❌ launcher CLI failed"
    exit 1
fi

# Test mcp-server help
echo "Testing mcp-server help..."
if python -m mcp_python_example.bin.mcp_server --help >/dev/null 2>&1; then
    echo "✅ mcp-server CLI works"
else
    echo "❌ mcp-server CLI failed"
    exit 1
fi

# Test mcp-client help
echo "Testing mcp-client help..."
if python -m mcp_python_example.bin.mcp_client --help >/dev/null 2>&1; then
    echo "✅ mcp-client CLI works"
else
    echo "❌ mcp-client CLI failed"
    exit 1
fi

echo ""
echo "========================================="
echo "✅ All tests completed successfully!"
echo "========================================="