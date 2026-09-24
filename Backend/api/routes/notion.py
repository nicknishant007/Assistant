from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
)

from fastapi.responses import RedirectResponse

from sqlalchemy.orm import Session

from database.session import get_db
from dependencies.auth import get_current_user

from config.settings import settings

from services.integration_service import (
    create_or_update_integration,
    get_notion_integration,
    disconnect_integration,
)

from services.notion.mcp_client import (
    NotionMCPClient,
)

from services.notion.oauth import (
    discover_mcp_oauth,
    generate_pkce,
    generate_state,
    register_mcp_client,
    build_authorization_url,
    exchange_code_for_tokens,
)


router = APIRouter(
    prefix="/api/notion",
    tags=["Notion"],
)


# =========================================================
# COOKIE HELPERS
# =========================================================

def _oauth_cookie_options():
    """
    Production HTTPS:
        secure=True

    Local development:
        secure=False
    """

    return {
        "max_age": 600,
        "httponly": True,
        "secure": (
            settings.NOTION_REDIRECT_URI
            .startswith("https://")
        ),
        "samesite": "lax",
        "path": "/api/notion",
    }


# =========================================================
# START NOTION OAUTH
# =========================================================

@router.get("/login")
async def login_notion(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    Start the hosted Notion MCP OAuth flow.

    Flow:

        Discover OAuth
            ↓
        Generate PKCE
            ↓
        Register MCP client
            ↓
        Get client_id
            ↓
        Build authorize URL
            ↓
        Redirect to Notion
    """

    try:

        # -------------------------------------------------
        # 1. Discover OAuth metadata
        # -------------------------------------------------

        metadata = await discover_mcp_oauth()

        # -------------------------------------------------
        # 2. Generate PKCE
        # -------------------------------------------------

        (
            code_verifier,
            code_challenge,
        ) = generate_pkce()

        # -------------------------------------------------
        # 3. Generate OAuth state
        # -------------------------------------------------

        state = generate_state()

        # -------------------------------------------------
        # 4. Dynamically register NuroFlow
        # -------------------------------------------------

        credentials = await register_mcp_client(
            metadata=metadata,
            redirect_uri=(
                settings.NOTION_REDIRECT_URI
            ),
        )

        client_id = credentials.get(
            "client_id"
        )

        if not client_id:

            raise RuntimeError(
                "Notion MCP registration did not "
                "return a client_id."
            )

        # -------------------------------------------------
        # 5. Build authorization URL
        # -------------------------------------------------

        authorization_url = (
            build_authorization_url(
                metadata=metadata,
                client_id=client_id,
                redirect_uri=(
                    settings.NOTION_REDIRECT_URI
                ),
                code_challenge=(
                    code_challenge
                ),
                state=state,
            )
        )

        # -------------------------------------------------
        # 6. Redirect user to Notion
        # -------------------------------------------------

        response = RedirectResponse(
            url=authorization_url,
            status_code=302,
        )

        cookie_options = (
            _oauth_cookie_options()
        )

        # -------------------------------------------------
        # 7. Store OAuth transaction state
        # -------------------------------------------------

        response.set_cookie(
            key="notion_oauth_state",
            value=state,
            **cookie_options,
        )

        response.set_cookie(
            key="notion_code_verifier",
            value=code_verifier,
            **cookie_options,
        )

        # client_id is not a user secret, but keeping it
        # HttpOnly prevents frontend JavaScript from
        # accessing the OAuth transaction data.
        response.set_cookie(
            key="notion_oauth_client_id",
            value=client_id,
            **cookie_options,
        )

        return response

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to start Notion OAuth: "
                f"{str(e)}"
            ),
        )


# =========================================================
# NOTION OAUTH CALLBACK
# =========================================================

@router.get("/callback")
async def callback_notion(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Complete the Notion MCP OAuth flow.

    Flow:

        Callback
            ↓
        Validate state
            ↓
        Read PKCE verifier
            ↓
        Read registered client_id
            ↓
        Discover OAuth metadata
            ↓
        Exchange authorization code
            ↓
        Store user's Notion tokens
            ↓
        Redirect to frontend
    """

    # -----------------------------------------------------
    # 1. Read callback parameters
    # -----------------------------------------------------

    code = request.query_params.get(
        "code"
    )

    returned_state = (
        request.query_params.get(
            "state"
        )
    )

    oauth_error = (
        request.query_params.get(
            "error"
        )
    )

    error_description = (
        request.query_params.get(
            "error_description"
        )
    )

    if oauth_error:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Notion OAuth failed: "
                f"{oauth_error} "
                f"{error_description or ''}"
            ),
        )

    if not code:

        raise HTTPException(
            status_code=400,
            detail=(
                "Authorization code missing."
            ),
        )

    if not returned_state:

        raise HTTPException(
            status_code=400,
            detail=(
                "OAuth state missing."
            ),
        )

    # -----------------------------------------------------
    # 2. Read OAuth transaction cookies
    # -----------------------------------------------------

    stored_state = (
        request.cookies.get(
            "notion_oauth_state"
        )
    )

    code_verifier = (
        request.cookies.get(
            "notion_code_verifier"
        )
    )

    client_id = (
        request.cookies.get(
            "notion_oauth_client_id"
        )
    )

    if not stored_state:

        raise HTTPException(
            status_code=400,
            detail=(
                "OAuth state cookie missing."
            ),
        )

    if not code_verifier:

        raise HTTPException(
            status_code=400,
            detail=(
                "PKCE code verifier missing."
            ),
        )

    if not client_id:

        raise HTTPException(
            status_code=400,
            detail=(
                "Registered Notion MCP client_id "
                "is missing."
            ),
        )

    # -----------------------------------------------------
    # 3. Validate OAuth state
    # -----------------------------------------------------

    if returned_state != stored_state:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid OAuth state."
            ),
        )

    # -----------------------------------------------------
    # 4. Discover OAuth metadata again
    # -----------------------------------------------------

    try:

        metadata = await discover_mcp_oauth()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to rediscover Notion OAuth "
                f"metadata: {str(e)}"
            ),
        )

    # -----------------------------------------------------
    # 5. Exchange authorization code
    # -----------------------------------------------------

    try:

        tokens = (
            await exchange_code_for_tokens(
                metadata=metadata,
                code=code,
                code_verifier=code_verifier,
                client_id=client_id,
                redirect_uri=(
                    settings.NOTION_REDIRECT_URI
                ),
                client_secret=None,
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Notion token exchange failed: "
                f"{str(e)}"
            ),
        )

    # -----------------------------------------------------
    # 6. Extract tokens
    # -----------------------------------------------------

    notion_access_token = (
        tokens.get(
            "access_token"
        )
    )

    notion_refresh_token = (
        tokens.get(
            "refresh_token"
        )
    )

    if not notion_access_token:

        raise HTTPException(
            status_code=400,
            detail=(
                "Notion access token missing "
                "from token response."
            ),
        )

    # -----------------------------------------------------
    # 7. Save user's Notion integration
    # -----------------------------------------------------

    try:

        create_or_update_integration(
            db=db,
            user_id=current_user.id,
            provider="notion",
            access_token=(
                notion_access_token
            ),
            refresh_token=(
                notion_refresh_token
            ),
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to save Notion "
                f"integration: {str(e)}"
            ),
        )

    # -----------------------------------------------------
    # 8. Redirect back to frontend
    # -----------------------------------------------------

    response = RedirectResponse(
        url=(
            f"{settings.FRONTEND_URL}"
            "/home"
        ),
        status_code=302,
    )

    # -----------------------------------------------------
    # 9. Remove temporary OAuth cookies
    # -----------------------------------------------------

    response.delete_cookie(
        key="notion_oauth_state",
        path="/api/notion",
    )

    response.delete_cookie(
        key="notion_code_verifier",
        path="/api/notion",
    )

    response.delete_cookie(
        key="notion_oauth_client_id",
        path="/api/notion",
    )

    return response


# =========================================================
# CONNECTION STATUS
# =========================================================

@router.get("/connection")
async def notion_connection(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return the current user's Notion connection state.
    """

    integration = get_notion_integration(
        db=db,
        user_id=current_user.id,
    )

    if not integration:

        return {
            "connected": False,
            "provider": "notion",
        }

    return {
        "connected": integration.connected,
        "provider": integration.provider,
    }


# =========================================================
# DISCONNECT
# =========================================================

@router.post("/disconnect")
async def disconnect_notion(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Disconnect the current user's Notion integration.
    """

    integration = get_notion_integration(
        db=db,
        user_id=current_user.id,
    )

    if (
        not integration
        or not integration.connected
    ):

        return {
            "connected": False,
            "provider": "notion",
        }

    disconnect_integration(
        db=db,
        user_id=current_user.id,
        provider="notion",
    )

    return {
        "connected": False,
        "provider": "notion",
    }


# =========================================================
# LIST MCP TOOLS
# =========================================================

@router.get("/tools")
async def list_notion_tools(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List tools available from the hosted Notion MCP.
    """

    integration = get_notion_integration(
        db=db,
        user_id=current_user.id,
    )

    if not integration:

        raise HTTPException(
            status_code=400,
            detail=(
                "Notion is not connected."
            ),
        )

    if not integration.connected:

        raise HTTPException(
            status_code=400,
            detail=(
                "Notion integration is disconnected."
            ),
        )

    client = NotionMCPClient(
        notion_token=(
            integration.access_token
        )
    )

    result = await client.list_tools()

    tools = []

    for tool in result.tools:

        if hasattr(
            tool,
            "model_dump",
        ):

            tools.append(
                tool.model_dump()
            )

        else:

            tools.append(
                {
                    "name": tool.name,
                    "description": (
                        tool.description
                    ),
                    "inputSchema": (
                        tool.inputSchema
                    ),
                }
            )

    return {
        "count": len(tools),
        "tools": tools,
    }


# =========================================================
# TEST TOOL ACCESS
# =========================================================

@router.get("/test-tool-access")
async def test_tool_access(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Directly test the notion-get-tool-access MCP tool.
    """

    integration = get_notion_integration(
        db=db,
        user_id=current_user.id,
    )

    if not integration:

        raise HTTPException(
            status_code=400,
            detail=(
                "Notion is not connected."
            ),
        )

    if not integration.connected:

        raise HTTPException(
            status_code=400,
            detail=(
                "Notion integration is disconnected."
            ),
        )

    client = NotionMCPClient(
        notion_token=(
            integration.access_token
        )
    )

    result = await client.call_tool(
        tool_name=(
            "notion-get-tool-access"
        ),
        arguments={},
    )

    if hasattr(
        result,
        "model_dump",
    ):

        return result.model_dump()

    return {
        "result": str(result)
    }


# =========================================================
# TEST SEARCH
# =========================================================

@router.get("/test-search")
async def test_notion_search(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Directly test the notion-search MCP tool.
    """

    integration = get_notion_integration(
        db=db,
        user_id=current_user.id,
    )

    if not integration:

        raise HTTPException(
            status_code=400,
            detail=(
                "Notion is not connected."
            ),
        )

    if not integration.connected:

        raise HTTPException(
            status_code=400,
            detail=(
                "Notion integration is disconnected."
            ),
        )

    client = NotionMCPClient(
        notion_token=(
            integration.access_token
        )
    )

    result = await client.call_tool(
        tool_name="notion-search",
        arguments={
            "query": "project",
        },
    )

    if hasattr(
        result,
        "model_dump",
    ):

        return result.model_dump()

    return {
        "result": str(result)
    }