"""
MCP Server implementation using the official Python SDK.

This server provides counter operations, sampling functionality,
and web endpoints with optional JWT authentication.
"""

import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any
from collections.abc import AsyncGenerator

import click
import mcp.types as types
import structlog
from mcp.server.lowlevel import Server
from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, Response
from starlette.routing import Mount, Route
from starlette.types import Receive, Scope, Send

from ..auth import AuthConfig, auth_middleware

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer(),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


class McpExampleServer:
    """MCP Server with example tools and counter functionality."""

    def __init__(self) -> None:
        self.counter = 0
        self.app = Server(
            name="pythonexam-server",
            version="1.0.0",
            instructions=(
                "This is an example MCP server built with the official Python SDK. "
                "It provides counter operations, echo functionality, and basic shell command execution."
            ),
        )
        self._setup_handlers()

    def _setup_handlers(self) -> None:
        """Set up MCP protocol handlers."""

        @self.app.list_tools()  # type: ignore[misc, no-untyped-call]
        async def list_tools() -> list[types.Tool]:
            """Return available tools."""
            return [
                types.Tool(
                    name="increment",
                    description="Increment the counter by 1",
                    inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
                ),
                types.Tool(
                    name="get_counter",
                    description="Get the current counter value",
                    inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
                ),
                types.Tool(
                    name="reset_counter",
                    description="Reset the counter to zero",
                    inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
                ),
                types.Tool(
                    name="test_sampling",
                    description="Test MCP sampling by asking the connected LLM to say 'Hi'",
                    inputSchema={"type": "object", "properties": {}, "additionalProperties": False},
                ),
            ]

        @self.app.call_tool()  # type: ignore[misc]
        async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.ContentBlock]:
            """Handle tool calls."""

            if name == "increment":
                self.counter += 1
                return [types.TextContent(type="text", text=f"Counter incremented to: {self.counter}")]

            elif name == "get_counter":
                return [types.TextContent(type="text", text=f"Current counter value: {self.counter}")]

            elif name == "reset_counter":
                self.counter = 0
                return [types.TextContent(type="text", text="Counter reset to 0")]

            elif name == "test_sampling":
                return await self._handle_sampling()

            else:
                raise ValueError(f"Unknown tool: {name}")

    async def _handle_sampling(self) -> list[types.ContentBlock]:
        """Handle MCP sampling test - asks the LLM to say 'Hi'."""
        logger.info("🔔 Sampling test requested - asking LLM to say 'Hi'")

        try:
            # Access the request context from the Server instance
            ctx = self.app.request_context

            # Request the client to perform LLM sampling
            logger.info("📤 Sending sampling request to client...")
            sampling_result = await ctx.session.create_message(
                messages=[
                    types.SamplingMessage(
                        role="user",
                        content=types.TextContent(
                            type="text",
                            text=(
                                "Please say 'Hi' in a friendly and creative way! "
                                "Also tell me what model you are. Be brief (1-2 sentences)."
                            ),
                        ),
                    )
                ],
                max_tokens=150,
                related_request_id=ctx.request_id,
            )

            # Extract the LLM's response
            if sampling_result.content.type == "text":
                llm_response = sampling_result.content.text
            else:
                llm_response = str(sampling_result.content)

            logger.info(f"✅ LLM sampling successful! Model: {sampling_result.model}")

            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"📡 MCP Sampling Test - SUCCESS!\n\n"
                        f"Model used: {sampling_result.model}\n\n"
                        f"🤖 LLM Response:\n{llm_response}\n\n"
                        f"✅ MCP sampling is working! The server successfully requested "
                        f"the client to perform an LLM inference."
                    ),
                )
            ]

        except Exception as e:
            logger.error(f"❌ Sampling failed: {e}", exc_info=True)
            return [
                types.TextContent(
                    type="text",
                    text=(
                        f"❌ MCP Sampling Test - FAILED\n\n"
                        f"Error: {str(e)}\n\n"
                        f"Note: Sampling requires MCP client support. "
                        f"Make sure your client supports the sampling feature and "
                        f"the server is properly initialized."
                    ),
                )
            ]


# Web route handlers
async def home_page(request: Request) -> HTMLResponse:
    """Serve the home page."""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>MCP Python Server</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .header { background: #f4f4f4; padding: 20px; border-radius: 5px; }
        .endpoint { background: #e8f5e8; padding: 10px; margin: 5px 0; border-radius: 3px; }
        .mcp { background: #e8e8f5; padding: 10px; margin: 5px 0; border-radius: 3px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 MCP Python Server</h1>
        <p>A combined MCP + Web server built with the official Python SDK</p>
    </div>

    <h2>🔧 MCP Protocol</h2>
    <div class="mcp">
        <strong>MCP Endpoint:</strong> <code>/mcp</code><br>
        <strong>Protocol:</strong> Streamable HTTP<br>
        <strong>Tools:</strong> increment, get_counter, reset_counter, test_sampling
    </div>

    <h2>🌐 Web API Endpoints</h2>
    <div class="endpoint"><a href="/health">GET /health</a> - Health check</div>
    <div class="endpoint"><a href="/api/status">GET /api/status</a> - Server status JSON</div>
    <div class="endpoint"><a href="/dashboard">GET /dashboard</a> - Admin dashboard</div>

    <h2>💡 How to Connect</h2>
    <p><strong>VS Code MCP:</strong> Already configured! Tools available as mcp_pythonexam_*</p>
    <p><strong>Web Browser:</strong> You're here! Try the endpoints above</p>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


async def health_check(request: Request) -> JSONResponse:
    """Health check endpoint."""
    return JSONResponse(
        {
            "status": "ok",
            "service": "MCP Python Server",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "mcp_endpoint": "/mcp",
            "tools": ["increment", "get_counter", "reset_counter", "test_sampling"],
        }
    )


async def api_status(request: Request) -> JSONResponse:
    """API status endpoint."""
    return JSONResponse(
        {
            "server": "mcp-python-server",
            "version": "1.0.0",
            "mcp": {"protocol": "streamable-http", "endpoint": "/mcp", "tools_count": 4},
            "web": {"endpoints": ["/web", "/health", "/api/status", "/dashboard"]},
        }
    )


async def dashboard(request: Request) -> HTMLResponse:
    """Admin dashboard."""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>MCP Server Dashboard</title>
    <style>
        body { font-family: monospace; margin: 40px; background: #1e1e1e; color: #d4d4d4; }
        .panel { background: #2d2d30; padding: 20px; margin: 10px 0; border-radius: 5px; }
        .status { color: #4ec9b0; }
        .endpoint { color: #dcdcaa; }
    </style>
</head>
<body>
    <h1>🎛️ MCP Server Dashboard</h1>

    <div class="panel">
        <h3>🟢 Server Status</h3>
        <div class="status">✅ MCP Server: Running</div>
        <div class="status">✅ Web Server: Running</div>
        <div class="status">✅ Tools: 4 loaded</div>
    </div>

    <div class="panel">
        <h3>🔧 MCP Tools</h3>
        <div class="endpoint">increment - Increment counter</div>
        <div class="endpoint">get_counter - Get counter value</div>
        <div class="endpoint">reset_counter - Reset counter</div>
        <div class="endpoint">test_sampling - Test MCP sampling</div>
    </div>

    <div class="panel">
        <h3>🌐 Web Endpoints</h3>
        <div class="endpoint">GET /web - Home page</div>
        <div class="endpoint">GET /health - Health check</div>
        <div class="endpoint">GET /api/status - Status API</div>
        <div class="endpoint">GET /dashboard - This dashboard</div>
        <div class="endpoint">POST /mcp - MCP protocol endpoint</div>
    </div>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@click.command()
@click.option("--port", default=None, type=int, help="Port to bind the server to (default: from config or 8080)")
@click.option("--host", default=None, help="Host to bind the server to (default: from config or 127.0.0.1)")
@click.option("--log-level", default="INFO", help="Logging level")
@click.option("--no-auth", is_flag=True, help="Disable authentication")
def main(port: int | None, host: str | None, log_level: str, no_auth: bool) -> None:
    """Main MCP server entry point."""

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("Starting MCP Python Example Server...")
    logger.info("Using official Python MCP SDK from https://github.com/modelcontextprotocol/python-sdk")

    # Load configuration from etc/config.ini
    config_port = 8080
    config_host = "127.0.0.1"

    try:
        import configparser
        from pathlib import Path

        config_file = Path("etc/config.ini")
        if config_file.exists():
            config = configparser.ConfigParser()
            config.read(config_file)

            if "server" in config:
                config_port = config.getint("server", "port", fallback=8080)
                config_host = config.get("server", "host", fallback="127.0.0.1")
                logger.info(f"📄 Loaded config from {config_file}")
    except Exception as e:
        logger.warning(f"⚠️ Could not read config file: {e}")

    # CLI arguments override config
    final_port = port if port is not None else config_port
    final_host = host if host is not None else config_host

    # Load authentication configuration
    auth_config = None
    if not no_auth:
        try:
            auth_config = AuthConfig.load()
            logger.info(f"🔐 Authentication enabled with {len(auth_config.authorized_tokens)} authorized users")
        except (FileNotFoundError, ValueError) as e:
            logger.warning(f"⚠️ Failed to load auth config: {e}. Running WITHOUT authentication!")
            logger.warning("⚠️ To enable authentication, create etc/config.ini using token-manager")
            auth_config = None
    else:
        logger.info("⚠️ Authentication disabled via --no-auth flag")

    # Create MCP server instance
    mcp_server = McpExampleServer()

    # Create session manager
    session_manager = StreamableHTTPSessionManager(
        app=mcp_server.app,
        json_response=False,  # Use SSE streaming
    )

    # MCP ASGI handler with authentication middleware
    async def handle_mcp_with_auth(scope: Scope, receive: Receive, send: Send) -> None:
        """Handle MCP requests with optional authentication."""

        # Skip auth for non-HTTP requests
        if scope["type"] != "http":
            await session_manager.handle_request(scope, receive, send)
            return

        # Get authorization header
        authorization_header = None
        for header_name, header_value in scope.get("headers", []):
            if header_name == b"authorization":
                authorization_header = header_value.decode()
                break

        # Authenticate if auth is enabled
        if auth_config is not None:
            try:
                await auth_middleware(auth_config, authorization_header)
            except ValueError as e:
                # Send 401 Unauthorized
                response = Response(content=str(e), status_code=401, headers={"content-type": "text/plain"})
                await response(scope, receive, send)
                return

        # Proceed with MCP handling
        await session_manager.handle_request(scope, receive, send)

    @asynccontextmanager
    async def lifespan(app: Starlette) -> AsyncGenerator[None, None]:
        """Application lifespan manager."""
        async with session_manager.run():
            logger.info("Session manager started")
            try:
                yield
            finally:
                logger.info("Session manager shutting down...")

    # Create Starlette application
    starlette_app = Starlette(
        debug=True,
        routes=[
            Route("/health", health_check, methods=["GET"]),
            Route("/api/status", api_status, methods=["GET"]),
            Route("/dashboard", dashboard, methods=["GET"]),
            Route("/web", home_page, methods=["GET"]),
            Mount("/mcp", app=handle_mcp_with_auth),
        ],
        lifespan=lifespan,
    )

    # Add CORS middleware
    app = CORSMiddleware(
        starlette_app,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE"],
        expose_headers=["Mcp-Session-Id"],
    )

    bind_address = f"{final_host}:{final_port}"

    # Log startup information
    logger.info(f"🚀 Combined MCP + Web Server running on http://{bind_address}")
    logger.info("📋 MCP Protocol:")
    logger.info(f"   Endpoint: http://{bind_address}/mcp")
    logger.info("   Tools: increment, get_counter, reset_counter, test_sampling")

    if auth_config:
        logger.info("   🔐 Authentication: ENABLED (Bearer token required)")
    else:
        logger.info("   ⚠️ Authentication: DISABLED (no users configured)")

    logger.info("🌐 Web Endpoints:")
    logger.info(f"   Home: http://{bind_address}/web")
    logger.info(f"   Health: http://{bind_address}/health")
    logger.info(f"   Dashboard: http://{bind_address}/dashboard")
    logger.info("")

    if not auth_config:
        logger.info("💡 To enable authentication:")
        logger.info("   python -m mcp_python_example.bin.token_manager add <username>")

    logger.info("💡 VS Code MCP: Already configured as mcp_pythonexam_* tools")
    logger.info(f"💡 Web Browser: Visit http://{bind_address}/web for web interface")
    logger.info("")
    logger.info("Press Ctrl+C to shutdown")

    # Start server
    import uvicorn

    uvicorn.run(app, host=final_host, port=final_port, log_level=log_level.lower())


if __name__ == "__main__":
    main()
