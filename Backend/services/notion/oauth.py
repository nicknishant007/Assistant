import base64
import hashlib
import secrets
from urllib.parse import urlencode

import httpx


MCP_SERVER_URL = "https://mcp.notion.com/mcp"
MCP_SERVER_ORIGIN = "https://mcp.notion.com"


# ============================================================
# DISCOVER NOTION MCP OAUTH
# ============================================================

async def discover_mcp_oauth() -> dict:
    """
    Discover OAuth metadata for the hosted Notion MCP server.

    Flow:

        Notion MCP
            ↓
        Protected Resource Metadata
            ↓
        Authorization Server
            ↓
        Authorization Server Metadata
    """

    # --------------------------------------------------------
    # 1. Protected Resource Metadata
    # --------------------------------------------------------

    protected_resource_url = (
        f"{MCP_SERVER_ORIGIN}/"
        ".well-known/oauth-protected-resource"
    )

    async with httpx.AsyncClient(
        timeout=20.0
    ) as client:

        response = await client.get(
            protected_resource_url
        )

        response.raise_for_status()

        protected_resource = response.json()

    # --------------------------------------------------------
    # 2. Find Authorization Server
    # --------------------------------------------------------

    authorization_servers = (
        protected_resource.get(
            "authorization_servers"
        )
    )

    if not authorization_servers:
        raise RuntimeError(
            "No authorization servers found "
            "for Notion MCP."
        )

    auth_server_url = (
        authorization_servers[0]
        .rstrip("/")
    )

    # --------------------------------------------------------
    # 3. Authorization Server Metadata
    # --------------------------------------------------------

    metadata_url = (
        f"{auth_server_url}/"
        ".well-known/oauth-authorization-server"
    )

    async with httpx.AsyncClient(
        timeout=20.0
    ) as client:

        response = await client.get(
            metadata_url
        )

        response.raise_for_status()

        metadata = response.json()

    # --------------------------------------------------------
    # 4. Validate required metadata
    # --------------------------------------------------------

    if not metadata.get(
        "authorization_endpoint"
    ):
        raise RuntimeError(
            "Notion MCP OAuth metadata is missing "
            "authorization_endpoint."
        )

    if not metadata.get(
        "token_endpoint"
    ):
        raise RuntimeError(
            "Notion MCP OAuth metadata is missing "
            "token_endpoint."
        )

    return metadata


# ============================================================
# PKCE
# ============================================================

def generate_pkce():
    """
    Generate PKCE code_verifier and S256 code_challenge.
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

    return (
        code_verifier,
        code_challenge,
    )


# ============================================================
# OAUTH STATE
# ============================================================

def generate_state() -> str:
    """
    Generate a cryptographically secure OAuth state.
    """

    return secrets.token_urlsafe(32)


# ============================================================
# DYNAMIC CLIENT REGISTRATION
# ============================================================

async def register_mcp_client(
    metadata: dict,
    redirect_uri: str,
) -> dict:
    """
    Dynamically register NuroFlow as an OAuth client
    for the hosted Notion MCP authorization server.

    The registration uses public-client authentication
    because token_endpoint_auth_method is set to "none".
    """

    registration_endpoint = (
        metadata.get(
            "registration_endpoint"
        )
    )

    if not registration_endpoint:
        raise RuntimeError(
            "Notion MCP does not expose a "
            "registration endpoint."
        )

    # --------------------------------------------------------
    # Registration payload
    # --------------------------------------------------------

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

    async with httpx.AsyncClient(
        timeout=20.0
    ) as client:

        response = await client.post(
            registration_endpoint,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": (
                    "application/json"
                ),
            },
        )

    if not response.is_success:

        raise RuntimeError(
            "Notion MCP client registration failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    credentials = response.json()

    client_id = credentials.get(
        "client_id"
    )

    if not client_id:

        raise RuntimeError(
            "Notion MCP registration did not "
            "return a client_id."
        )

    return credentials


# ============================================================
# BUILD AUTHORIZATION URL
# ============================================================

def build_authorization_url(
    metadata: dict,
    client_id: str,
    redirect_uri: str,
    code_challenge: str,
    state: str,
) -> str:
    """
    Build the Notion MCP authorization URL.
    """

    authorization_endpoint = (
        metadata.get(
            "authorization_endpoint"
        )
    )

    if not authorization_endpoint:

        raise RuntimeError(
            "Missing authorization_endpoint "
            "from Notion MCP metadata."
        )

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": "",
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
        "prompt": "consent",
    }

    return (
        f"{authorization_endpoint}"
        f"?{urlencode(params)}"
    )


# ============================================================
# EXCHANGE AUTHORIZATION CODE
# ============================================================

async def exchange_code_for_tokens(
    metadata: dict,
    code: str,
    code_verifier: str,
    client_id: str,
    redirect_uri: str,
    client_secret: str | None = None,
) -> dict:
    """
    Exchange the authorization code for
    Notion MCP access/refresh tokens.
    """

    token_endpoint = (
        metadata.get(
            "token_endpoint"
        )
    )

    if not token_endpoint:

        raise RuntimeError(
            "Missing token_endpoint "
            "from Notion MCP metadata."
        )

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code_verifier": code_verifier,
    }

    if client_secret:

        data["client_secret"] = (
            client_secret
        )

    async with httpx.AsyncClient(
        timeout=20.0
    ) as client:

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
            "Notion token exchange failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    tokens = response.json()

    if not tokens.get(
        "access_token"
    ):

        raise RuntimeError(
            "Notion token response did not "
            "contain an access_token."
        )

    return tokens


# ============================================================
# REFRESH ACCESS TOKEN
# ============================================================

async def refresh_access_token(
    metadata: dict,
    refresh_token: str,
    client_id: str,
    client_secret: str | None = None,
) -> dict:
    """
    Refresh an expired Notion MCP access token.
    """

    token_endpoint = (
        metadata.get(
            "token_endpoint"
        )
    )

    if not token_endpoint:

        raise RuntimeError(
            "Missing token_endpoint "
            "from Notion MCP metadata."
        )

    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
    }

    if client_secret:

        data["client_secret"] = (
            client_secret
        )

    async with httpx.AsyncClient(
        timeout=20.0
    ) as client:

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
            "Notion token refresh failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    tokens = response.json()

    if not tokens.get(
        "access_token"
    ):

        raise RuntimeError(
            "Notion refresh response did not "
            "contain an access_token."
        )

    return tokens


# ============================================================
# INTROSPECTION
# ============================================================

async def introspect_access_token(
    metadata: dict,
    access_token: str,
) -> dict:
    """
    Kept for compatibility with the existing codebase.

    Notion MCP may not expose token introspection.
    """

    introspection_endpoint = (
        metadata.get(
            "introspection_endpoint"
        )
    )

    if not introspection_endpoint:

        raise RuntimeError(
            "Notion MCP does not expose "
            "an introspection endpoint."
        )

    async with httpx.AsyncClient(
        timeout=20.0
    ) as client:

        response = await client.post(
            introspection_endpoint,
            data={
                "token": access_token,
                "token_type_hint": (
                    "access_token"
                ),
            },
            headers={
                "Accept": "application/json",
                "Content-Type": (
                    "application/x-www-form-urlencoded"
                ),
            },
        )

    response.raise_for_status()

    return response.json()