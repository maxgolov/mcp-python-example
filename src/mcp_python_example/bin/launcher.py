"""
Process launcher for MCP Python Example.

Manages starting, stopping, and checking status of the MCP server process.
"""

import logging
import os
import platform
import subprocess  # nosec B404 - subprocess needed for process management
import sys
import time
from pathlib import Path

import click
import psutil

logger = logging.getLogger(__name__)

PID_FILE = "mcp-server.pid"
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "mcp-server.log"
ERROR_LOG_FILE = LOG_DIR / "mcp-server-error.log"


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"


def get_server_pid() -> int | None:
    """Get the server PID from the PID file."""
    pid_file = Path(PID_FILE)

    if not pid_file.exists():
        return None

    try:
        pid_str = pid_file.read_text().strip()
        return int(pid_str)
    except (ValueError, FileNotFoundError):
        return None


def is_process_running(pid: int) -> bool:
    """Check if a process is running by PID."""
    try:
        process = psutil.Process(pid)
        return bool(process.is_running())
    except psutil.NoSuchProcess:
        return False


def is_server_running() -> bool:
    """Check if the MCP server is running."""
    pid = get_server_pid()
    if pid is None:
        return False

    return is_process_running(pid)


def start_server(host: str, port: int) -> None:
    """Start the MCP server in background."""
    if is_server_running():
        click.echo("🟢 MCP server is already running!")
        return

    click.echo("🚀 Starting MCP server in background...")

    # Create logs directory
    LOG_DIR.mkdir(exist_ok=True)

    # Find Python executable (prefer venv if available)
    project_root = Path(__file__).parent.parent.parent.parent
    venv_python = (
        project_root / ".venv" / "Scripts" / "python.exe" if is_windows() else project_root / ".venv" / "bin" / "python"
    )
    python_exe = str(venv_python) if venv_python.exists() else sys.executable

    # Prepare command
    cmd = [python_exe, "-m", "mcp_python_example.bin.mcp_server", "--host", host, "--port", str(port)]

    # Setup environment with PYTHONPATH
    env = os.environ.copy()
    env["PYTHONPATH"] = str(project_root / "src")

    # Setup log files
    with open(LOG_FILE, "a") as log_file, open(ERROR_LOG_FILE, "a") as err_file:
        # Platform-specific process creation
        if is_windows():
            # Windows: Use CREATE_NEW_PROCESS_GROUP to detach
            process = subprocess.Popen(  # nosec B603
                cmd,
                stdout=log_file,
                stderr=err_file,
                stdin=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                env=env,
                cwd=Path.cwd(),
            )
        else:
            # Unix: Use start_new_session to detach
            process = subprocess.Popen(  # nosec B603
                cmd,
                stdout=log_file,
                stderr=err_file,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                env=env,
                cwd=Path.cwd(),
            )

    pid = process.pid

    # Save PID to file for tracking
    Path(PID_FILE).write_text(str(pid))

    # Give the server a moment to start
    time.sleep(3)

    if is_server_running():
        click.echo("✅ MCP server started successfully!")
        click.echo(f"   URL: http://{host}:{port}/mcp")
        click.echo(f"   PID: {pid}")
        click.echo(f"   Logs: {LOG_FILE}")
        click.echo(f"   Errors: {ERROR_LOG_FILE}")
        click.echo()
        click.echo("💡 Use 'launcher status' to check server status")
        click.echo("💡 Use 'launcher stop' to stop the server")
    else:
        click.echo(f"❌ Failed to start server. Check {ERROR_LOG_FILE} for details")


def stop_server() -> None:
    """Stop the MCP server."""
    pid_file = Path(PID_FILE)

    if not pid_file.exists():
        click.echo("❌ No PID file found. Server might not be running or was started manually.")
        return

    pid = get_server_pid()
    if pid is None:
        click.echo("❌ Could not read PID from file.")
        return

    click.echo(f"🛑 Stopping MCP server (PID: {pid})...")

    try:
        process = psutil.Process(pid)

        # Terminate gracefully first
        process.terminate()

        # Wait up to 10 seconds for graceful shutdown
        try:
            process.wait(timeout=10)
            click.echo("✅ Server stopped successfully")
        except psutil.TimeoutExpired:
            # Force kill if graceful shutdown fails
            click.echo("⚠️ Forcing server shutdown...")
            process.kill()
            process.wait(timeout=5)
            click.echo("✅ Server forcefully stopped")

    except psutil.NoSuchProcess:
        click.echo("⚠️ Process not found (may have already stopped)")

    except psutil.AccessDenied:
        click.echo("❌ Access denied when trying to stop process")
        return

    except Exception as e:
        click.echo(f"❌ Error stopping server: {e}")
        return

    # Remove PID file
    try:
        pid_file.unlink()
    except FileNotFoundError:
        pass


def check_server_status() -> None:
    """Check and display server status."""
    if is_server_running():
        pid = get_server_pid()
        click.echo(f"🟢 MCP server is running (PID: {pid})")
        click.echo("   URL: http://127.0.0.1:8080/mcp")

        # Check if we can reach the server
        click.echo("   Checking connectivity...")

        try:
            import httpx

            # Simple HTTP check
            response = httpx.get("http://127.0.0.1:8080/health", timeout=5.0)
            if response.status_code == 200:
                click.echo("   ✅ Server is responding to HTTP requests")
            else:
                click.echo(f"   ⚠️ Server responded with status {response.status_code}")

        except Exception:
            click.echo("   ⚠️ Could not test server connectivity")

    else:
        click.echo("🔴 MCP server is not running")


@click.command()
@click.argument("action", type=click.Choice(["start", "stop", "status", "restart"]))
@click.option("--port", default=8080, help="Port to bind the server to")
@click.option("--host", default="127.0.0.1", help="Host to bind the server to")
@click.option("--log-level", default="INFO", help="Logging level")
def main(action: str, port: int, host: str, log_level: str) -> None:
    """Process launcher for MCP server."""

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    if action == "start":
        start_server(host, port)
    elif action == "stop":
        stop_server()
    elif action == "status":
        check_server_status()
    elif action == "restart":
        stop_server()
        time.sleep(2)
        start_server(host, port)


if __name__ == "__main__":
    main()
