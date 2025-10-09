"""
Authentication module for MCP Python Example.

Handles JWT token authentication and configuration file management.
"""

import configparser
import logging
from datetime import datetime, timezone
from pathlib import Path

import jwt
from pydantic import BaseModel

logger = logging.getLogger(__name__)

CONFIG_PATH = "etc/config.ini"


class TokenClaims(BaseModel):
    """JWT token claims structure."""

    sub: str  # Subject (username)
    iat: int  # Issued at timestamp
    exp: int  # Expiry timestamp
    iss: str  # Issuer


class AuthConfig:
    """Authentication configuration manager."""

    def __init__(self, jwt_secret: str, authorized_tokens: dict[str, str]):
        self.jwt_secret = jwt_secret
        self.authorized_tokens = authorized_tokens

    @classmethod
    def load(cls) -> "AuthConfig":
        """Load authentication configuration from file."""
        config_file = Path(CONFIG_PATH)

        if not config_file.exists():
            raise FileNotFoundError(
                f"Config file not found at: {CONFIG_PATH}\nPlease create it or disable authentication."
            )

        config = configparser.ConfigParser()
        config.read(CONFIG_PATH)

        # Get JWT secret
        if "server" not in config or "jwt_secret" not in config["server"]:
            raise ValueError("JWT secret not found in config")

        jwt_secret = config["server"]["jwt_secret"]

        # Get authorized tokens
        authorized_tokens = {}
        if "auth" in config:
            for username, token in config["auth"].items():
                if not username.startswith("#") and token:
                    authorized_tokens[username] = token

        return cls(jwt_secret=jwt_secret, authorized_tokens=authorized_tokens)

    def verify_token(self, token: str) -> TokenClaims:
        """
        Verify a JWT token.

        First checks if token exists in authorized list,
        then verifies JWT signature and expiry.
        """
        # Check if token exists in authorized list
        is_authorized = token in self.authorized_tokens.values()

        if not is_authorized:
            raise ValueError("Token not in authorized list")

        # Verify JWT signature and expiry
        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"], issuer="mcp-python-example")

            return TokenClaims(**payload)

        except jwt.InvalidTokenError as e:
            raise ValueError(f"Token verification failed: {e}") from e


async def auth_middleware(auth_config: AuthConfig | None, authorization_header: str | None) -> TokenClaims | None:
    """
    Authentication middleware for validating bearer tokens.

    Args:
        auth_config: Authentication configuration (None if auth disabled)
        authorization_header: Authorization header value

    Returns:
        TokenClaims if authentication successful, None if auth disabled

    Raises:
        ValueError: If authentication fails
    """
    # If no auth config, authentication is disabled
    if auth_config is None:
        return None

    # Get Authorization header
    if not authorization_header:
        raise ValueError("Missing Authorization header")

    # Extract bearer token
    if not authorization_header.startswith("Bearer "):
        raise ValueError("Invalid Authorization header format")

    token = authorization_header[7:]  # Remove "Bearer " prefix

    # Verify token
    try:
        claims = auth_config.verify_token(token)

        # Log successful authentication
        issued_at = datetime.fromtimestamp(claims.iat, timezone.utc)
        logger.info(f"Authenticated request from user: {claims.sub} (issued: {issued_at.isoformat()})")

        return claims

    except ValueError as e:
        logger.warning(f"Authentication failed: {e}")
        raise


def create_empty_config() -> None:
    """Create an empty configuration file template."""
    config_file = Path(CONFIG_PATH)
    config_file.parent.mkdir(parents=True, exist_ok=True)

    config = configparser.ConfigParser()
    config["server"] = {
        "port": "8080",
        "host": "127.0.0.1",
        "jwt_secret": "mcp-python-example-secret-change-in-production",
    }
    config["auth"] = {"# Add users here using token-manager": ""}

    with open(config_file, "w") as f:
        config.write(f)

    logger.info(f"Created empty config file at: {CONFIG_PATH}")
