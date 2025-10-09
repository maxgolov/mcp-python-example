"""
Smoke test for MCP Python Example server functionality.
"""

import pytest
from mcp_python_example.bin.mcp_server import McpExampleServer


def test_server_creation() -> None:
    """Test that server can be created and has expected structure."""
    server = McpExampleServer()

    # Test server has the required components
    assert hasattr(server, "counter")
    assert hasattr(server, "app")
    assert server.counter == 0

    # Test server app has expected attributes
    assert server.app.name == "pythonexam-server"
    assert server.app.version == "1.0.0"
    if server.app.instructions:
        assert "example MCP server" in server.app.instructions

    print("✅ Server creation works correctly")


def test_counter_state() -> None:
    """Test counter state management."""
    server = McpExampleServer()

    # Test initial counter state
    assert server.counter == 0

    # Test direct counter manipulation (for unit testing)
    server.counter += 5
    assert server.counter == 5

    server.counter = 0
    assert server.counter == 0

    print("✅ Counter state management works correctly")


def test_server_configuration() -> None:
    """Test server configuration and metadata."""
    server = McpExampleServer()

    # Verify server configuration
    assert server.app.name == "pythonexam-server"
    assert server.app.version == "1.0.0"
    if server.app.instructions:
        assert len(server.app.instructions) > 0

    print("✅ Server configuration is correct")


def test_import() -> None:
    """Test that imports work correctly."""
    from mcp_python_example import __version__
    from mcp_python_example import auth  # noqa: F401
    from mcp_python_example.bin import launcher, mcp_client, mcp_server, token_manager  # noqa: F401

    assert __version__ == "0.1.0"
    print("✅ All imports successful")


def test_auth_module() -> None:
    """Test auth module functionality."""
    from mcp_python_example.auth import TokenClaims, AuthConfig, auth_middleware

    # Test TokenClaims model
    claims = TokenClaims(sub="testuser", iat=1234567890, exp=9999999999, iss="test")

    assert claims.sub == "testuser"
    assert claims.iat == 1234567890
    assert claims.exp == 9999999999
    assert claims.iss == "test"

    # Test AuthConfig
    config = AuthConfig(jwt_secret="test-secret", authorized_tokens={"user1": "token123", "user2": "token456"})

    assert config.jwt_secret == "test-secret"
    assert config.authorized_tokens == {"user1": "token123", "user2": "token456"}

    # Test auth_middleware function exists and is callable
    assert callable(auth_middleware)

    print("✅ Auth module works correctly")
