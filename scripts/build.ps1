# Minimal PowerShell Build Script for MCP Python Example
# Usage: .\scripts\build.ps1

Write-Host "Building MCP Python Example..." -ForegroundColor Cyan
python -m pip install --upgrade pip build
python -m build
Write-Host "✅ Build complete! Check dist/ folder" -ForegroundColor Green
