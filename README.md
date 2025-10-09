# MCP Python Example

A complete MCP (Model Context Protocol) HTTP server implementation using the official Python SDK.

This project replicates the functionality of [mcp-rust-example](https://github.com/top-5/mcp-rust-example) using Python, providing:

- **HTTP MCP Server** with authentication
- **Tool System** with counter operations
- **MCP Sampling** support for LLM interactions  
- **Web Interface** for monitoring and health checks
- **Authentication** via JWT tokens
- **Process Management** with launcher utility
- **Client Implementation** for testing

## Features

### 🔧 MCP Tools
- `increment` - Increment the counter by 1
- `get_counter` - Get the current counter value  
- `reset_counter` - Reset the counter to zero
- `test_sampling` - Test MCP sampling by asking the connected LLM to say 'Hi'

### 🌐 Web Endpoints
- `/web` - Home page with server information
- `/health` - Health check endpoint
- `/api/status` - Server status JSON API
- `/dashboard` - Admin dashboard
- `/mcp` - MCP protocol endpoint (HTTP Streamable)

### 🔐 Authentication
- JWT-based authentication with configurable users
- Bearer token authorization for MCP endpoints  
- Token management utilities
- Configuration-based user management

## Quick Start

### Prerequisites
- Python 3.10 or later
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/top-5/mcp-python-example
   cd mcp-python-example
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .venv\Scripts\activate
   
   # Unix/macOS
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -e .
   ```

### Usage

#### Starting the Server

**Option 1: Direct start**
```bash
mcp-server --port 8080 --host 127.0.0.1
```

**Option 2: Using launcher (background process)**
```bash
launcher start --port 8080
launcher status
launcher stop
```

#### Authentication Setup

1. **Generate authentication tokens**
   ```bash
   token-manager add testuser
   ```

2. **List users**
   ```bash
   token-manager list
   ```

3. **Get VS Code configuration**
   ```bash
   token-manager show-config testuser
   ```

#### Testing with MCP Client

```bash
mcp-client --url http://127.0.0.1:8080/mcp
```

## Project Structure

```
mcp-python-example/
├── src/
│   └── mcp_python_example/
│       ├── __init__.py
│       ├── auth.py              # Authentication module
│       └── bin/                 # Executable scripts
│           ├── __init__.py
│           ├── mcp_server.py    # Main MCP server
│           ├── launcher.py      # Process launcher
│           ├── token_manager.py # Token management
│           └── mcp_client.py    # Test client
├── etc/
│   └── config.ini              # Configuration file
├── logs/                       # Server logs
├── scripts/                    # Build scripts
│   ├── build.sh               # Build script
│   └── test.sh                # Test script
├── .vscode/
│   ├── mcp.json              # VS Code MCP configuration
│   └── settings.json         # VS Code settings
├── .github/
│   └── workflows/
│       └── ci.yml            # GitHub Actions CI
└── pyproject.toml            # Python project configuration
```

## Development

### Building
```bash
./scripts/build.sh
```

### Testing  
```bash
./scripts/test.sh
```

### Code Quality
```bash
ruff check src tests
ruff format src tests
mypy src
```

## Configuration

The server uses `etc/config.ini` for configuration:

```ini
[server]
port=8080
host=127.0.0.1
jwt_secret=your-secret-key

[auth]
testuser=your-jwt-token
```

## VS Code Integration

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "pythonexam": {
      "url": "http://127.0.0.1:8080/mcp",
      "type": "http",
      "headers": {
        "Authorization": "Bearer your-jwt-token"
      }
    }
  }
}
```

## API Documentation

### MCP Protocol Endpoint

**URL**: `POST /mcp`  
**Protocol**: [MCP Streamable HTTP](https://modelcontextprotocol.io/docs/specification/transport/http-sse)  
**Authentication**: Bearer token (optional)

### Web API Endpoints

- `GET /web` - Home page
- `GET /health` - Health check (`{"status": "ok", ...}`)  
- `GET /api/status` - Server status JSON
- `GET /dashboard` - Admin dashboard

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## Support

- [Issue Tracker](https://github.com/top-5/mcp-python-example/issues)
- [MCP Documentation](https://modelcontextprotocol.io/)
- [Python SDK Documentation](https://github.com/modelcontextprotocol/python-sdk)