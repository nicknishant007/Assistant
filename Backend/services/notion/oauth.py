import base64
import hashlib
import secrets
from urllib.parse import urlencode

import httpx


MCP_SERVER_URL = "https://mcp.notion.com/mcp"
MCP_SERVER_ORIGIN = "https://mcp.notion.com"


async def discover_mcp_oauth() -> dict:
    """
    Discover the OAuth configuration for Notion MCP.

    Flow:
        MCP server
            ↓
        Protected Resource Metadata
            ↓
        Authorization Server
            ↓
        Authorization Server Metadata
    """

    # RFC 9470
    protected_resource_url = (
        f"{MCP_SERVER_ORIGIN}/"
        ".well-known/oauth-protected-resource"
    )

    async with httpx.AsyncClient() as client:

        response = await client.get(
            protected_resource_url
        )

        response.raise_for_status()

        protected_resource = response.json()

        authorization_servers = (
            protected_resource.get(
                "authorization_servers"
            )
        )

        if not authorization_servers:
            raise RuntimeError(
                "No authorization servers found"
            )

        auth_server_url = authorization_servers[0].rstrip("/")

        # RFC 8414
        metadata_url = (
            f"{auth_server_url}/"
            ".well-known/oauth-authorization-server"
        )

        response = await client.get(
            metadata_url
        )

        response.raise_for_status()

        metadata = response.json()

        if not metadata.get("authorization_endpoint"):
            raise RuntimeError(
                "Missing authorization_endpoint"
            )

        if not metadata.get("token_endpoint"):
            raise RuntimeError(
                "Missing token_endpoint"
            )

        return metadata


def generate_pkce():
    """
    Generate PKCE verifier and S256 challenge.
    """

    code_verifier = (
        base64.urlsafe_b64encode(
            secrets.token_bytes(32)
        )
        .decode()
        .rstrip("=")
    )

    digest = hashlib.sha256(
        code_verifier.encode()
    ).digest()

    code_challenge = (
        base64.urlsafe_b64encode(
            digest
        )
        .decode()
        .rstrip("=")
    )

    return code_verifier, code_challenge


def generate_state() -> str:
    """
    Generate OAuth CSRF state.
    """

    return secrets.token_urlsafe(32)


async def register_mcp_client(
    metadata: dict,
    redirect_uri: str,
) -> dict:
    """
    Dynamically register NuroFlow as an MCP OAuth client.
    """

    registration_endpoint = metadata.get(
        "registration_endpoint"
    )

    if not registration_endpoint:
        raise RuntimeError(
            "Notion MCP does not expose "
            "a registration endpoint"
        )

    payload = {
        "client_name": "NuroFlow",
        "redirect_uris": [
            redirect_uri
        ],
        "grant_types": [
            "authorization_code",
            "refresh_token",
        ],
        "response_types": [
            "code"
        ],
        "token_endpoint_auth_method": "none",
    }

    async with httpx.AsyncClient() as client:

        response = await client.post(
            registration_endpoint,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
        )

        if not response.is_success:
            raise RuntimeError(
                "MCP client registration failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        credentials = response.json()

    if not credentials.get("client_id"):
        raise RuntimeError(
            "No client_id returned from "
            "Notion MCP registration"
        )

    return credentials


def build_authorization_url(
    metadata: dict,
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    state: str,
) -> str:
    """
    Build the Notion OAuth authorization URL.
    """

    authorization_endpoint = metadata.get(
        "authorization_endpoint"
    )

    if not authorization_endpoint:
        raise RuntimeError(
            "Missing authorization_endpoint"
        )

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "prompt": "consent",
    }

    return (
        f"{authorization_endpoint}"
        f"?{urlencode(params)}"
    )


async def exchange_code_for_tokens(
    metadata: dict,
    code: str,
    code_verifier: str,
    client_id: str,
    redirect_uri: str,
    client_secret: str | None = None,
) -> dict:
    """
    Exchange the authorization code
    for Notion MCP access/refresh tokens.
    """

    token_endpoint = metadata.get(
        "token_endpoint"
    )

    if not token_endpoint:
        raise RuntimeError(
            "Missing token_endpoint"
        )

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }

    if client_secret:
        data["client_secret"] = client_secret

    async with httpx.AsyncClient() as client:

        response = await client.post(
            token_endpoint,
            data=data,
            headers={
                "Accept": "application/json",
                "Content-Type": (
                    "application/x-www-form-urlencoded"
                ),
            },
        )

        if not response.is_success:
            raise RuntimeError(
                "Token exchange failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        tokens = response.json()

    if not tokens.get("access_token"):
        raise RuntimeError(
            "Notion token response did not "
            "contain access_token"
        )

    return tokens


async def refresh_access_token(
    metadata: dict,
    refresh_token: str,
    client_id: str,
    client_secret: str | None = None,
) -> dict:
    """
    Refresh an expired Notion MCP access token.
    """

    token_endpoint = metadata.get(
        "token_endpoint"
    )

    if not token_endpoint:
        raise RuntimeError(
            "Missing token_endpoint"
        )

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }

    if client_secret:
        data["client_secret"] = client_secret

    async with httpx.AsyncClient() as client:

        response = await client.post(
            token_endpoint,
            data=data,
            headers={
                "Accept": "application/json",
                "Content-Type": (
                    "application/x-www-form-urlencoded"
                ),
            },
        )

        if not response.is_success:
            raise RuntimeError(
                "Token refresh failed: "
                f"{response.status_code} "
                f"{response.text}"
            )

        return response.json()