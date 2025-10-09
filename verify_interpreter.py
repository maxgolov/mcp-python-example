"""
VS Code Python interpreter verification script.
Run this to check if VS Code is using the right Python interpreter.
"""

import sys
import os
from pathlib import Path

def main() -> None:
    """Verify Python interpreter setup."""
    print("🔍 Python Interpreter Verification")
    print("=" * 50)
    
    print(f"🐍 Python executable: {sys.executable}")
    print(f"🐍 Python version: {sys.version}")
    print(f"📁 Current working directory: {os.getcwd()}")
    
    # Check if we're in virtual environment
    venv_path = Path(sys.executable).parent.parent
    if venv_path.name == ".venv":
        print("✅ Using virtual environment")
        print(f"📦 Virtual env path: {venv_path}")
    else:
        print("⚠️  Not using virtual environment")
    
    # Check PYTHONPATH
    pythonpath = sys.path
    print(f"🛤️  Python path entries: {len(pythonpath)}")
    
    src_in_path = any("src" in p for p in pythonpath)
    if src_in_path:
        print("✅ Source directory in Python path")
    else:
        print("⚠️  Source directory not in Python path")
    
    # Try importing our package
    try:
        import mcp_python_example
        print("✅ Can import mcp_python_example")
        print(f"📍 Package location: {mcp_python_example.__file__}")
    except ImportError as e:
        print(f"❌ Cannot import mcp_python_example: {e}")
    
    # Try importing MCP SDK
    try:
        import mcp
        print("✅ Can import mcp SDK")
    except ImportError as e:
        print(f"❌ Cannot import mcp SDK: {e}")

if __name__ == "__main__":
    main()