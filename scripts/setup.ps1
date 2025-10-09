# PowerShell Setup Script for MCP Python Example
# Usage: .\scripts\setup.ps1 [-Dev]

param(
    [switch]$Dev,           # Install development dependencies
    [switch]$Force,         # Force recreate virtual environment
    [switch]$Help           # Show help
)

if ($Help) {
    Write-Host @"
MCP Python Example Setup Script

USAGE:
    .\scripts\setup.ps1 [OPTIONS]

OPTIONS:
    -Dev       Install development dependencies (default: production only)
    -Force     Force recreate virtual environment
    -Help      Show this help message

EXAMPLES:
    .\scripts\setup.ps1                    # Production setup
    .\scripts\setup.ps1 -Dev               # Development setup
    .\scripts\setup.ps1 -Dev -Force        # Force recreate dev environment

"@
    exit 0
}

# Script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot ".venv"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MCP Python Example Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"
Write-Host "Python version: $(python --version 2>$null)"
Write-Host ""

Set-Location $ProjectRoot

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    if (-not $pythonVersion) {
        throw "Python not found"
    }
    Write-Host "✅ Python found: $pythonVersion"
} catch {
    Write-Host "❌ Python not found. Please install Python 3.10+ and add it to PATH" -ForegroundColor Red
    exit 1
}

# Handle virtual environment
if ($Force -and (Test-Path $VenvPath)) {
    Write-Host "🗑️ Removing existing virtual environment..."
    Remove-Item -Recurse -Force $VenvPath
}

if (-not (Test-Path $VenvPath)) {
    Write-Host "🔧 Creating virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "📦 Virtual environment already exists"
}

# Activate virtual environment
Write-Host "📦 Activating virtual environment..."
$ActivateScript = Join-Path $VenvPath "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
} else {
    Write-Host "❌ Failed to find activation script" -ForegroundColor Red
    exit 1
}

# Upgrade pip
Write-Host "📈 Upgrading pip..."
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to upgrade pip" -ForegroundColor Red
    exit 1
}

# Install dependencies
if ($Dev) {
    Write-Host "📦 Installing development dependencies..."
    pip install -e .[dev]
} else {
    Write-Host "📦 Installing production dependencies..."
    pip install -e .
}

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Verify installation
Write-Host ""
Write-Host "🧪 Verifying installation..."

$testCommands = @(
    @("mcp-server --help", "MCP Server CLI"),
    @("launcher --help", "Launcher CLI"),
    @("token-manager --help", "Token Manager CLI"),
    @("mcp-client --help", "MCP Client CLI")
)

foreach ($test in $testCommands) {
    $command = $test[0]
    $name = $test[1]
    
    try {
        Invoke-Expression $command *>$null
        Write-Host "✅ $name works" -ForegroundColor Green
    } catch {
        Write-Host "❌ $name failed" -ForegroundColor Red
    }
}

# Development tools verification
if ($Dev) {
    Write-Host ""
    Write-Host "🔍 Verifying development tools..."
    
    $devTools = @(
        @("ruff --version", "Ruff"),
        @("mypy --version", "MyPy"),
        @("pytest --version", "PyTest")
    )
    
    foreach ($tool in $devTools) {
        $command = $tool[0]
        $name = $tool[1]
        
        try {
            Invoke-Expression $command *>$null
            Write-Host "✅ $name available" -ForegroundColor Green
        } catch {
            Write-Host "❌ $name not available" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "NEXT STEPS:"
Write-Host "1. Run: mcp-server --help                    # See server options"
Write-Host "2. Run: launcher --help                      # See launcher options"  
Write-Host "3. Run: token-manager --help                 # See auth management"
if ($Dev) {
    Write-Host "4. Run: .\scripts\test.ps1                   # Run tests (coming soon)"
    Write-Host "5. Run: ruff check src                       # Check code"
    Write-Host "6. Run: mypy src                             # Type check"
}
Write-Host ""