"""
Token Manager for MCP Python Example.

Manages JWT tokens for server authentication.
"""

import configparser
import logging
import secrets
from datetime import datetime, timezone
from pathlib import Path

import click
import jwt

from ..auth import CONFIG_PATH, create_empty_config

logger = logging.getLogger(__name__)


def load_config() -> configparser.ConfigParser:
    """Load configuration from file."""
    config_file = Path(CONFIG_PATH)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found at: {CONFIG_PATH}\nPlease create it first.")

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    return config


def save_config(config: configparser.ConfigParser) -> None:
    """Save configuration to file."""
    config_file = Path(CONFIG_PATH)
    config_file.parent.mkdir(parents=True, exist_ok=True)

    with open(config_file, "w") as f:
        config.write(f)


def get_jwt_secret(config: configparser.ConfigParser) -> str:
    """Get JWT secret from config."""
    if "server" not in config or "jwt_secret" not in config["server"]:
        raise ValueError("JWT secret not found in config")

    return config["server"]["jwt_secret"]


def generate_token(username: str, secret: str) -> str:
    """Generate a JWT token for the given username."""
    # Token expires on December 31, 2099
    exp = datetime(2099, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)

    payload = {"sub": username, "iat": int(now.timestamp()), "exp": int(exp.timestamp()), "iss": "mcp-python-example"}

    token = jwt.encode(payload, secret, algorithm="HS256")
    return token


def print_vscode_config(token: str) -> None:
    """Print VS Code MCP configuration."""
    config_text = f"""Add this to .vscode/mcp.json:

{{
  "servers": {{
    "pythonexam": {{
      "url": "http://127.0.0.1:8080/mcp",
      "type": "http",
      "headers": {{
        "Authorization": "Bearer {token}"
      }}
    }}
  }},
  "inputs": []
}}"""
    print(config_text)


@click.group()
@click.option("--log-level", default="INFO", help="Logging level")
def cli(log_level: str) -> None:
    """Manage MCP server authentication tokens."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


@cli.command()
@click.argument("username")
def add(username: str) -> None:
    """Add a new user and generate their JWT token."""
    try:
        config = load_config()
    except FileNotFoundError:
        # Create empty config if it doesn't exist
        create_empty_config()
        config = load_config()

    secret = get_jwt_secret(config)

    # Ensure auth section exists
    if "auth" not in config:
        config.add_section("auth")

    # Check if user already exists
    if config.has_option("auth", username):
        click.echo(f"User '{username}' already exists. Use 'remove' first if you want to regenerate.", err=True)
        raise click.Abort()

    # Generate token
    token = generate_token(username, secret)

    # Save to config
    config.set("auth", username, token)
    save_config(config)

    click.echo(f"✅ User '{username}' added successfully!")
    click.echo()
    click.echo("📋 Token generated:")
    click.echo(token)
    click.echo()
    click.echo("🔧 Add this to your .vscode/settings.json:")
    click.echo()
    print_vscode_config(token)


@cli.command()
def list() -> None:
    """List all authorized users."""
    try:
        config = load_config()
    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        return

    click.echo("📋 Authorized Users:")
    click.echo()

    if "auth" not in config:
        click.echo("  No users configured yet.")
        click.echo()
        click.echo("💡 Add a user with: token-manager add <username>")
        return

    users = []
    for username in config.options("auth"):
        if not username.startswith("#"):
            token = config.get("auth", username)
            if token:
                users.append((username, token))

    users.sort(key=lambda x: x[0])

    if not users:
        click.echo("  No users configured yet.")
        click.echo()
        click.echo("💡 Add a user with: token-manager add <username>")
    else:
        for username, token in users:
            click.echo(f"  • {username}")
            click.echo(f"    Token: {token[:20]}...")

        click.echo()
        click.echo(f"Total: {len(users)} user(s)")


@cli.command()
@click.argument("username")
def remove(username: str) -> None:
    """Remove a user."""
    try:
        config = load_config()
    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        return

    if "auth" not in config or not config.has_option("auth", username):
        click.echo(f"❌ User '{username}' not found", err=True)
        raise click.Abort()

    config.remove_option("auth", username)
    save_config(config)

    click.echo(f"✅ User '{username}' removed successfully!")


@cli.command(name="rotate-secret")
def rotate_secret() -> None:
    """Rotate the JWT secret (invalidates all existing tokens)."""
    click.echo("⚠️  WARNING: Rotating JWT secret will invalidate ALL existing tokens!")
    click.echo("   All users will need new tokens.")
    click.echo()

    if not click.confirm("Continue?"):
        click.echo("Cancelled.")
        return

    try:
        config = load_config()
    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        return

    # Generate new secret (64 character hex string)
    new_secret = secrets.token_hex(32)

    # Ensure server section exists
    if "server" not in config:
        config.add_section("server")

    config.set("server", "jwt_secret", new_secret)

    # Clear all user tokens
    if "auth" in config:
        config.remove_section("auth")
        config.add_section("auth")
        config.set("auth", "# Add users here using token-manager", "")

    save_config(config)

    click.echo("✅ JWT secret rotated successfully!")
    click.echo(f"   New secret: {new_secret}")
    click.echo()
    click.echo("⚠️  All user tokens have been cleared.")
    click.echo("   Re-add users with: token-manager add <username>")


@cli.command(name="show-config")
@click.argument("username")
def show_config(username: str) -> None:
    """Show VS Code configuration for a user."""
    try:
        config = load_config()
    except FileNotFoundError as e:
        click.echo(f"❌ {e}", err=True)
        return

    if "auth" not in config or not config.has_option("auth", username):
        click.echo(f"❌ User '{username}' not found", err=True)
        raise click.Abort()

    token = config.get("auth", username)

    click.echo(f"🔧 VS Code Configuration for user '{username}':")
    click.echo()
    print_vscode_config(token)


def main() -> None:
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
