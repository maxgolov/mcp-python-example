# MCP Python Example VS Code Configuration

This directory contains VS Code configuration for the MCP Python Example project.

## Files

### `mcp.json`
MCP (Model Context Protocol) configuration for VS Code. This file configures VS Code to connect to the local MCP server for enhanced coding assistance.

**Features:**
- Connects to local MCP server at `http://127.0.0.1:8080/mcp`
- Uses HTTP transport with authentication
- Provides MCP tools as `mcp_pythonexam_*` commands in VS Code

### `settings.json`
VS Code workspace settings for Python development.

**Features:**
- Configures Python interpreter to use project's `.venv`
- Enables strict type checking with MyPy
- Configures Ruff for linting and formatting
- Sets up pytest for testing
- Excludes build artifacts and cache files

## Usage

1. **Start the MCP server:**
   ```bash
   # Method 1: Direct start
   mcp-server --port 8080

   # Method 2: Using launcher
   launcher start --port 8080
   ```

2. **Open VS Code in project directory:**
   ```bash
   code .
   ```

3. **MCP tools will be available as:**
   - `mcp_pythonexam_increment` - Increment counter
   - `mcp_pythonexam_get_counter` - Get counter value  
   - `mcp_pythonexam_reset_counter` - Reset counter
   - `mcp_pythonexam_test_sampling` - Test MCP sampling

## Authentication

The MCP configuration uses a JWT token for authentication. To regenerate or create new tokens:

```bash
# Add a new user
token-manager add <username>

# Show VS Code config for a user  
token-manager show-config <username>
```

## Troubleshooting

### MCP Server Not Connecting
1. Check server is running: `launcher status`
2. Verify URL in `mcp.json` matches server address
3. Ensure authentication token is valid

### Python Environment Issues
1. Activate virtual environment: `source .venv/bin/activate` (Linux/macOS) or `.venv\Scripts\activate` (Windows)
2. Install dependencies: `pip install -e .[dev]`
3. Reload VS Code window: `Ctrl+Shift+P` → "Developer: Reload Window"

### Type Checking Errors
1. Install dependencies: `pip install -e .[dev]`
2. Run type checker manually: `mypy src`
3. Check Python interpreter setting in VS Code