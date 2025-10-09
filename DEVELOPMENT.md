# Development Setup Guide

This guide explains how to set up a development environment for the MCP Python Example project.

## Prerequisites

- **Python 3.10 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads/)

## Quick Start

### Option 1: Automated Setup (Recommended)

#### Windows (PowerShell)
```powershell
# Development setup
.\scripts\setup.ps1 -Dev

# Production setup  
.\scripts\setup.ps1
```

#### Cross-Platform (Python)
```bash
# Development setup
python scripts/setup.py --dev

# Production setup
python scripts/setup.py
```

#### Unix/Linux/macOS (Bash)
```bash
# Make executable and run
chmod +x scripts/build.sh
./scripts/build.sh
```

### Option 2: Manual Setup

#### 1. Clone and Navigate
```bash
git clone <repository-url>
cd mcp-python-example
```

#### 2. Create Virtual Environment
```bash
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Unix/Linux/macOS)
source .venv/bin/activate
```

#### 3. Install Dependencies

**Development Mode:**
```bash
pip install -e .[dev]
```

**Production Mode:**
```bash
pip install -e .
```

**Using Requirements Files:**
```bash
# Development
pip install -r requirements-dev.txt

# Production only
pip install -r requirements-prod.txt
```

## Project Structure

```
mcp-python-example/
├── src/
│   └── mcp_python_example/       # Main package
│       ├── auth.py               # Authentication utilities
│       └── bin/                  # CLI scripts
│           ├── mcp_server.py     # MCP HTTP server
│           ├── mcp_client.py     # Test client
│           ├── launcher.py       # Process launcher
│           └── token_manager.py  # Auth token management
├── scripts/                      # Setup and build scripts
│   ├── setup.py                  # Cross-platform setup
│   ├── setup.ps1                 # Windows PowerShell setup
│   ├── build.sh                  # Unix build script
│   └── test.sh                   # Unix test script
├── tests/                        # Test files
├── etc/                          # Configuration files
├── logs/                         # Log files
├── pyproject.toml                # Modern Python packaging
├── requirements-prod.txt         # Production dependencies
├── requirements-dev.txt          # Development dependencies
└── README.md                     # Main documentation
```

## Available CLI Tools

After installation, these commands are available:

- **`mcp-server`** - Start the MCP HTTP server
- **`launcher`** - Process launcher and manager  
- **`token-manager`** - JWT token management
- **`mcp-client`** - Test client for the server

### Examples

```bash
# Start server on port 8080
mcp-server --port 8080

# Launch server in background
launcher start

# Generate auth token
token-manager generate-token --user alice

# Test client connection
mcp-client --url http://localhost:8080/mcp
```

## Development Workflow

### 1. Code Quality Checks

```bash
# Format code
ruff format src tests

# Lint code
ruff check src tests

# Type checking
mypy src

# Run all checks
ruff format src tests && ruff check src tests && mypy src
```

### 2. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_basic.py -v
```

### 3. Building

```bash
# Build distribution packages
python -m build

# Install from source
pip install -e .
```

## Environment Configuration

### Authentication Setup

1. Create configuration directory:
```bash
mkdir -p etc
```

2. Generate JWT secret and config:
```bash
token-manager init-config
```

3. Create users:
```bash
token-manager create-user --username alice --roles user,admin
```

### Environment Variables

Set these in your environment or `.env` file:

```bash
# Server Configuration
MCP_HOST=127.0.0.1
MCP_PORT=8080
MCP_LOG_LEVEL=INFO

# Authentication (optional)
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# Development
PYTHONPATH=src
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure virtual environment is activated
2. **Permission Errors**: Run as administrator on Windows or use `sudo` on Unix
3. **Port Conflicts**: Use `--port` to specify different port
4. **Missing Dependencies**: Run setup script again or reinstall

### Development Tips

- Use `pip install -e .` for editable installs during development
- Run `mypy src` regularly to catch type errors
- Use `ruff check --fix src` to auto-fix many linting issues
- Check `logs/` directory for runtime error logs

### Getting Help

```bash
# Command help
mcp-server --help
launcher --help
token-manager --help

# Version info
python -c "import mcp_python_example; print(mcp_python_example.__version__)"
```

## IDE Setup

### VS Code

Recommended extensions:
- Python
- Pylance (for type checking)
- Ruff (for linting and formatting)

Settings (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.ruffEnabled": true,
    "python.formatting.provider": "ruff",
    "python.analysis.typeCheckingMode": "strict"
}
```

### PyCharm

1. Open project directory
2. Configure Python interpreter to use `.venv/bin/python`
3. Enable code inspections for type hints
4. Configure Ruff as external tool

## Deployment

### Docker (Coming Soon)

```dockerfile
FROM python:3.12-slim
COPY requirements-prod.txt .
RUN pip install -r requirements-prod.txt
COPY . .
RUN pip install .
CMD ["mcp-server"]
```

### Systemd Service (Linux)

```ini
[Unit]
Description=MCP Python Example Server
After=network.target

[Service]
Type=simple
User=mcp
WorkingDirectory=/opt/mcp-python-example
Environment=PATH=/opt/mcp-python-example/.venv/bin
ExecStart=/opt/mcp-python-example/.venv/bin/mcp-server
Restart=always

[Install]
WantedBy=multi-user.target
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`  
3. Install dev dependencies: `./scripts/setup.ps1 -Dev`
4. Make changes and ensure tests pass: `pytest`
5. Run quality checks: `ruff check src && mypy src`
6. Commit changes: `git commit -m 'Add amazing feature'`
7. Push to branch: `git push origin feature/amazing-feature`
8. Open a Pull Request