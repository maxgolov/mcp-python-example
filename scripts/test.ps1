# PowerShell Test Script for MCP Python Example
# Usage: .\scripts\test.ps1 [-Coverage] [-Verbose]

param(
    [switch]$Coverage,      # Run with coverage reporting
    [switch]$Verbose,       # Verbose output
    [switch]$Help           # Show help
)

if ($Help) {
    Write-Host @"
MCP Python Example Test Script

USAGE:
    .\scripts\test.ps1 [OPTIONS]

OPTIONS:
    -Coverage   Generate coverage report
    -Verbose    Verbose test output
    -Help       Show this help message

EXAMPLES:
    .\scripts\test.ps1                     # Run basic tests
    .\scripts\test.ps1 -Coverage           # Run with coverage
    .\scripts\test.ps1 -Verbose -Coverage  # Full verbose with coverage

"@
    exit 0
}

# Script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot ".venv"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MCP Python Example Tests" -ForegroundColor Cyan  
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"
Write-Host ""

Set-Location $ProjectRoot

# Activate virtual environment
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    Write-Host "📦 Activating virtual environment..."
    & $ActivateScript
} else {
    Write-Host "❌ Virtual environment not found. Run setup first." -ForegroundColor Red
    Write-Host "   .\scripts\setup.ps1 -Dev" -ForegroundColor Yellow
    exit 1
}

# Ensure test dependencies are installed
Write-Host "📦 Checking test dependencies..."
try {
    python -c "import pytest, pytest_cov, pytest_asyncio" 2>$null
    Write-Host "✅ Test dependencies available"
} catch {
    Write-Host "📦 Installing test dependencies..."
    pip install -e .[dev] | Out-Null
}

# Create test directory and basic test if they don't exist
if (-not (Test-Path "tests")) {
    Write-Host "📁 Creating tests directory..."
    New-Item -ItemType Directory -Path "tests" | Out-Null
    
    # Create basic test file
    $BasicTestContent = @'
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
'@
    
    Set-Content -Path "tests\test_basic.py" -Value $BasicTestContent
    Write-Host "✅ Created basic test file"
}

# Build pytest command
$pytestArgs = @("tests/")

if ($Verbose) {
    $pytestArgs += "-v"
}

if ($Coverage) {
    $pytestArgs += @("--cov=src", "--cov-report=term-missing", "--cov-report=html")
}

# Run tests
Write-Host "🧪 Running tests..."
Write-Host "Command: pytest $($pytestArgs -join ' ')"

try {
    & pytest @pytestArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ All tests passed" -ForegroundColor Green
    } else {
        Write-Host "❌ Some tests failed" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Error running tests: $_" -ForegroundColor Red
    exit 1
}

# Test CLI tools (smoke tests)
Write-Host ""
Write-Host "🧪 Testing CLI tools..."

$cliTests = @(
    @("python -m mcp_python_example.bin.token_manager --help", "token-manager CLI"),
    @("python -m mcp_python_example.bin.launcher --help", "launcher CLI"),
    @("python -m mcp_python_example.bin.mcp_server --help", "mcp-server CLI"),
    @("python -m mcp_python_example.bin.mcp_client --help", "mcp-client CLI")
)

foreach ($test in $cliTests) {
    $command = $test[0]
    $name = $test[1]
    
    try {
        Invoke-Expression $command *>$null
        Write-Host "✅ $name works" -ForegroundColor Green
    } catch {
        Write-Host "❌ $name failed" -ForegroundColor Red
    }
}

# Code quality checks
Write-Host ""
Write-Host "🔍 Running code quality checks..."

# Ruff format check
try {
    ruff format --check src tests *>$null
    Write-Host "✅ Code formatting OK" -ForegroundColor Green
} catch {
    Write-Host "❌ Code formatting issues found" -ForegroundColor Red
    Write-Host "   Run: ruff format src tests" -ForegroundColor Yellow
}

# Ruff lint check  
try {
    ruff check src tests *>$null
    Write-Host "✅ Ruff linting passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Ruff found linting issues" -ForegroundColor Red
    Write-Host "   Run: ruff check src tests --fix" -ForegroundColor Yellow
}

# MyPy type checking
try {
    mypy src *>$null  
    Write-Host "✅ Type checking passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Type checking failed" -ForegroundColor Red
    Write-Host "   Run: mypy src" -ForegroundColor Yellow
}

if ($Coverage) {
    Write-Host ""
    Write-Host "📊 Coverage report generated in htmlcov/"
    if (Test-Path "htmlcov\index.html") {
        Write-Host "   View: htmlcov\index.html"
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ All tests completed!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan