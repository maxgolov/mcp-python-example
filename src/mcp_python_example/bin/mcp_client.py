"""
MCP Client implementation for testing the Python MCP server.

This client connects to the MCP server and tests various tools.
"""

import asyncio
import logging

import click
import httpx
from mcp.client.session import ClientSession
from mcp.client.streamable_http import streamablehttp_client
from mcp import types

logger = logging.getLogger(__name__)


async def test_mcp_server(server_url: str, auth_token: str | None = None) -> None:
    """Test the MCP server functionality."""

    logger.info(f"🔌 Connecting to MCP server at: {server_url}")

    # Set up headers
    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    # Create client session using streamablehttp_client
    async with streamablehttp_client(server_url, headers=headers) as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            # Initialize the session
            await session.initialize()

            logger.info("✅ Connected to MCP server!")

            # List available tools
            logger.info("🔧 Fetching available tools...")
            tools_result = await session.list_tools()

            logger.info(f"📋 Available tools ({len(tools_result.tools)} total):")
            for tool in tools_result.tools:
                description = tool.description if tool.description else "No description"
                logger.info(f"   - {tool.name}: {description}")

            # Test counter operations
            logger.info("🧪 Testing tools...")

            # Get initial counter value
            logger.info("Getting initial counter value...")
            result = await session.call_tool("get_counter", {})

            if result.content:
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        logger.info(f"📊 {content.text}")

            # Increment counter a few times
            for i in range(1, 4):
                logger.info(f"Incrementing counter ({i})...")
                result = await session.call_tool("increment", {})

                if result.content:
                    for content in result.content:
                        if isinstance(content, types.TextContent):
                            logger.info(f"✅ {content.text}")

            # Test sampling (if supported)
            try:
                logger.info("Testing MCP sampling...")
                result = await session.call_tool("test_sampling", {})

                if result.content:
                    for content in result.content:
                        if isinstance(content, types.TextContent):
                            logger.info(f"🎯 Sampling result: {content.text}")

            except Exception as e:
                logger.warning(f"⚠️ Sampling test failed (expected if not supported): {e}")

            # Reset counter
            logger.info("Resetting counter...")
            result = await session.call_tool("reset_counter", {})

            if result.content:
                for content in result.content:
                    if isinstance(content, types.TextContent):
                        logger.info(f"🔄 {content.text}")

    logger.info("✅ Client test completed successfully!")


@click.command()
@click.option("--url", default="http://127.0.0.1:8080/mcp", help="MCP server URL")
@click.option("--token", help="Authentication token (Bearer)")
@click.option("--log-level", default="INFO", help="Logging level")
def main(url: str, token: str | None, log_level: str) -> None:
    """MCP client for testing the Python MCP server."""

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Test server connectivity first
    logger.info("🔍 Testing server connectivity...")

    try:
        # Quick HTTP health check
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        # Extract base URL for health check
        if url.endswith("/mcp"):
            base_url = url[:-4]  # Remove /mcp suffix
            health_url = f"{base_url}/health"
        else:
            # Assume URL is base URL
            health_url = f"{url}/health"
            url = f"{url}/mcp"  # Add MCP endpoint

        response = httpx.get(health_url, timeout=10.0)
        if response.status_code == 200:
            logger.info("✅ Server is responding to HTTP requests")
        else:
            logger.warning(f"⚠️ Server health check returned status {response.status_code}")

    except Exception as e:
        logger.warning(f"⚠️ Could not reach server health endpoint: {e}")
        logger.info("Proceeding with MCP connection test...")

    # Run the MCP client test
    try:
        asyncio.run(test_mcp_server(url, token))
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Client test failed: {e}")
        raise click.Abort() from e


if __name__ == "__main__":
    main()
