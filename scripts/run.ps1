# PowerShell Run Script for MCP Python Example
# Usage: .\scripts\run.ps1 [-Port 8080] [-HostAddress "127.0.0.1"] [-NoAuth]

param(
    [int]$Port = 8080,                    # Server port (default: 8080)
    [string]$HostAddress = "127.0.0.1",   # Server host (default: 127.0.0.1)
    [switch]$NoAuth,                      # Disable authentication
    [string]$LogLevel = "INFO",           # Log level: DEBUG, INFO, WARNING, ERROR
    [switch]$Help                         # Show help
)

if ($Help) {
    Write-Host @"
MCP Python Example Run Script

USAGE:
    .\scripts\run.ps1 [OPTIONS]

OPTIONS:
    -Port <port>          Server port (default: 8080)
    -HostAddress <host>   Server host (default: 127.0.0.1)
    -NoAuth               Disable authentication
    -LogLevel <level>     Log level: DEBUG, INFO, WARNING, ERROR (default: INFO)
    -Help                 Show this help message

EXAMPLES:
    .\scripts\run.ps1                                    # Start server on 127.0.0.1:8080
    .\scripts\run.ps1 -Port 3000                         # Start on port 3000
    .\scripts\run.ps1 -Port 8080 -NoAuth                 # Start without auth
    .\scripts\run.ps1 -Port 8080 -LogLevel DEBUG         # Start with debug logging

CONFIGURATION:
    The server reads configuration from etc/config.ini
    Use token-manager to manage authentication tokens

"@
    exit 0
}

# Script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$VenvPath = Join-Path $ProjectRoot ".venv"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "MCP Python Example Server" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot"
Write-Host "Server: http://${HostAddress}:${Port}"
Write-Host "Authentication: $(if ($NoAuth) { 'Disabled' } else { 'Enabled' })"
Write-Host "Log level: $LogLevel"
Write-Host ""

Set-Location $ProjectRoot

# Check if virtual environment exists
if (-not (Test-Path $VenvPath)) {
    Write-Host "❌ Virtual environment not found. Please run setup first:" -ForegroundColor Red
    Write-Host "   .\scripts\setup.ps1 -Dev" -ForegroundColor Yellow
    exit 1
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

# Check if config file exists (when auth is enabled)
$ConfigPath = Join-Path $ProjectRoot "etc\config.ini"
if (-not $NoAuth -and -not (Test-Path $ConfigPath)) {
    Write-Host "⚠️  Configuration file not found: $ConfigPath" -ForegroundColor Yellow
    Write-Host "   Creating default config..." -ForegroundColor Yellow
    
    # Ensure etc directory exists
    $EtcDir = Join-Path $ProjectRoot "etc"
    if (-not (Test-Path $EtcDir)) {
        New-Item -ItemType Directory -Path $EtcDir | Out-Null
    }
    
    # Create default config
    @"
[server]
port = $Port
host = $HostAddress
jwt_secret = mcp-python-example-secret-change-in-production

[auth]
# Add users here using token-manager CLI
# Example: user1 = <jwt-token>

"@ | Out-File -FilePath $ConfigPath -Encoding UTF8
    
    Write-Host "✅ Created default configuration" -ForegroundColor Green
    Write-Host "   Use 'token-manager' to add users and manage authentication" -ForegroundColor Cyan
}

# Build command
$ServerCommand = "mcp-server --port $Port --host $HostAddress --log-level $LogLevel"

if ($NoAuth) {
    $ServerCommand += " --no-auth"
}

Write-Host ""
Write-Host "🚀 Starting MCP Server..." -ForegroundColor Green
Write-Host "Command: $ServerCommand" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Run the server
try {
    Invoke-Expression $ServerCommand
} catch {
    Write-Host ""
    Write-Host "❌ Server stopped with error: $_" -ForegroundColor Red
    exit 1
}
