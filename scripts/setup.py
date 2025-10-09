#!/usr/bin/env python3
"""
Cross-platform setup script for MCP Python Example.

This script sets up the development or production environment
for the MCP Python Example project.
"""

import argparse
import os
import platform
import subprocess
import sys
from pathlib import Path


import sys
import subprocess
import argparse
from pathlib import Path
from typing import Any

def run_command(cmd: list[str], check: bool = True, capture_output: bool = False) -> subprocess.CompletedProcess[str]:
    """Run a command and handle errors."""
    try:
        result = subprocess.run(
            cmd, 
            check=check, 
            capture_output=capture_output, 
            text=True,
            shell=sys.platform == "win32"
        )
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Command failed: {' '.join(cmd)}")
        print(f"Error: {e}")
        sys.exit(1)


def check_python_version() -> None:
    """Check if Python version is compatible."""
    if sys.version_info < (3, 10):
        print(f"❌ Python 3.10+ required, but got {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} found")


def create_venv(venv_path: Path, force: bool = False) -> None:
    """Create virtual environment."""
    if force and venv_path.exists():
        print("🗑️ Removing existing virtual environment...")
        import shutil
        shutil.rmtree(venv_path)
    
    if not venv_path.exists():
        print("🔧 Creating virtual environment...")
        run_command([sys.executable, "-m", "venv", str(venv_path)])
    else:
        print("📦 Virtual environment already exists")


def get_python_executable(venv_path: Path) -> Path:
    """Get the Python executable path in the virtual environment."""
    if platform.system() == "Windows":
        return venv_path / "Scripts" / "python.exe"
    else:
        return venv_path / "bin" / "python"


def install_dependencies(python_exe: Path, dev: bool = False) -> None:
    """Install project dependencies."""
    print("📈 Upgrading pip...")
    run_command([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])
    
    if dev:
        print("📦 Installing development dependencies...")
        run_command([str(python_exe), "-m", "pip", "install", "-e", ".[dev]"])
    else:
        print("📦 Installing production dependencies...")
        run_command([str(python_exe), "-m", "pip", "install", "-e", "."])


def verify_installation(python_exe: Path, dev: bool = False) -> None:
    """Verify that installation was successful."""
    print("🧪 Verifying installation...")
    
    # Test CLI commands
    test_commands = [
        (f"{python_exe} -m mcp_python_example.bin.mcp_server --help", "MCP Server CLI"),
        (f"{python_exe} -m mcp_python_example.bin.launcher --help", "Launcher CLI"),
        (f"{python_exe} -m mcp_python_example.bin.token_manager --help", "Token Manager CLI"),
        (f"{python_exe} -m mcp_python_example.bin.mcp_client --help", "MCP Client CLI"),
    ]
    
    for command, name in test_commands:
        try:
            run_command(command.split(), capture_output=True)
            print(f"✅ {name} works")
        except subprocess.CalledProcessError:
            print(f"❌ {name} failed")
    
    # Test development tools if in dev mode
    if dev:
        print("🔍 Verifying development tools...")
        dev_tools = [
            (f"{python_exe} -m ruff --version", "Ruff"),
            (f"{python_exe} -m mypy --version", "MyPy"),
            (f"{python_exe} -m pytest --version", "PyTest"),
        ]
        
        for command, name in dev_tools:
            try:
                run_command(command.split(), capture_output=True)
                print(f"✅ {name} available")
            except subprocess.CalledProcessError:
                print(f"❌ {name} not available")


def main() -> None:
    """Main setup function."""
    parser = argparse.ArgumentParser(
        description="Setup MCP Python Example development environment"
    )
    parser.add_argument(
        "--dev", 
        action="store_true", 
        help="Install development dependencies"
    )
    parser.add_argument(
        "--force", 
        action="store_true", 
        help="Force recreate virtual environment"
    )
    parser.add_argument(
        "--venv-dir",
        default=".venv",
        help="Virtual environment directory name (default: .venv)"
    )
    
    args = parser.parse_args()
    
    # Project paths
    project_root = Path(__file__).parent.parent
    venv_path = project_root / args.venv_dir
    
    print("=========================================")
    print("MCP Python Example Setup")
    print("=========================================")
    print(f"Project root: {project_root}")
    print(f"Platform: {platform.system()}")
    print("")
    
    os.chdir(project_root)
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    create_venv(venv_path, args.force)
    
    # Get Python executable
    python_exe = get_python_executable(venv_path)
    
    # Install dependencies
    install_dependencies(python_exe, args.dev)
    
    # Verify installation
    verify_installation(python_exe, args.dev)
    
    print("")
    print("=========================================")
    print("✅ Setup completed successfully!")
    print("=========================================")
    print("")
    print("NEXT STEPS:")
    print(f"1. Activate environment:")
    if platform.system() == "Windows":
        print(f"   .venv\\Scripts\\activate")
    else:
        print(f"   source .venv/bin/activate")
    print(f"2. Run server: mcp-server --help")
    print(f"3. Run launcher: launcher --help")
    print(f"4. Manage tokens: token-manager --help")
    
    if args.dev:
        print(f"5. Run tests: python -m pytest")
        print(f"6. Check code: ruff check src")
        print(f"7. Type check: mypy src")


if __name__ == "__main__":
    main()