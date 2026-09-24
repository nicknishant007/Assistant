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
)

from services.notion.mcp_client import (
    NotionMCPClient,
)

from services.notion.oauth import (
    discover_mcp_oauth,
    generate_pkce,
    generate_state,
    build_authorization_url,
    exchange_code_for_tokens,
)


router = APIRouter(
    prefix="/api/notion",
    tags=["Notion"],
)


# ---------------------------------------------------------
# START NOTION OAUTH
# ---------------------------------------------------------

@router.get("/login")
async def login_notion(
    request: Request,
    current_user=Depends(get_current_user),
):
    """
    Start the Notion MCP OAuth flow.

    User must already be logged into NuroFlow.
    """

    # 1. Discover Notion OAuth metadata
    metadata = await discover_mcp_oauth()

    # 2. Generate PKCE
    code_verifier, code_challenge = generate_pkce()

    # 3. Generate OAuth state
    state = generate_state()

    # 4. Build Notion authorization URL
    authorization_url = build_authorization_url(
        metadata=metadata,
        client_id=settings.NOTION_MCP_CLIENT_ID,
        redirect_uri=settings.NOTION_REDIRECT_URI,
        code_challenge=code_challenge,
        state=state,
    )

    # 5. Redirect user to Notion
    response = RedirectResponse(
        url=authorization_url,
        status_code=302,
    )

    # Store temporary OAuth data.
    #
    # These cookies are short-lived and HTTP-only.
    # For production at scale, you can move these
    # into server-side session/Redis storage.
    response.set_cookie(
        key="notion_oauth_state",
        value=state,
        max_age=600,
        httponly=True,
        secure=True,      # True in production HTTPS
        samesite="none",
        path="/",
    )

    response.set_cookie(
        key="notion_code_verifier",
        value=code_verifier,
        max_age=600,
        httponly=True,
        secure=False,      # True in production HTTPS
        samesite="lax",
        path="/",
    )

    return response


# ---------------------------------------------------------
# NOTION OAUTH CALLBACK
# ---------------------------------------------------------

@router.get("/callback")
async def callback_notion(
    request: Request,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Handle the callback from Notion.
    """

    # -----------------------------------------------------
    # 1. Read callback parameters
    # -----------------------------------------------------

    code = request.query_params.get("code")
    returned_state = request.query_params.get("state")
    oauth_error = request.query_params.get("error")
    error_description = request.query_params.get(
        "error_description"
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
            detail="Authorization code missing",
        )

    if not returned_state:
        raise HTTPException(
            status_code=400,
            detail="OAuth state missing",
        )

    # -----------------------------------------------------
    # 2. Retrieve state + PKCE verifier
    # -----------------------------------------------------

    stored_state = request.cookies.get(
        "notion_oauth_state"
    )

    code_verifier = request.cookies.get(
        "notion_code_verifier"
    )

    if not stored_state:
        raise HTTPException(
            status_code=400,
            detail="OAuth state cookie missing",
        )

    if not code_verifier:
        raise HTTPException(
            status_code=400,
            detail="PKCE code verifier missing",
        )

    # -----------------------------------------------------
    # 3. Validate state
    # -----------------------------------------------------

    if returned_state != stored_state:
        raise HTTPException(
            status_code=400,
            detail="Invalid OAuth state",
        )

    # -----------------------------------------------------
    # 4. Discover OAuth metadata again
    # -----------------------------------------------------

    metadata = await discover_mcp_oauth()

    # -----------------------------------------------------
    # 5. Exchange authorization code for tokens
    # -----------------------------------------------------

    tokens = await exchange_code_for_tokens(
        metadata=metadata,
        code=code,
        code_verifier=code_verifier,
        client_id=settings.NOTION_MCP_CLIENT_ID,
        client_secret=settings.NOTION_MCP_CLIENT_SECRET,
        redirect_uri=settings.NOTION_REDIRECT_URI,
    )

    notion_access_token = tokens.get(
        "access_token"
    )

    notion_refresh_token = tokens.get(
        "refresh_token"
    )

    if not notion_access_token:
        raise HTTPException(
            status_code=400,
            detail="Notion access token missing",
        )

    # -----------------------------------------------------
    # 6. Save user's Notion integration
    # -----------------------------------------------------

    create_or_update_integration(
        db=db,
        user_id=current_user.id,
        provider="notion",
        access_token=notion_access_token,
        refresh_token=notion_refresh_token,
    )

    # -----------------------------------------------------
    # 7. Remove temporary OAuth cookies
    # -----------------------------------------------------

    response = RedirectResponse(
        url=f"{settings.FRONTEND_URL}/home",
        status_code=302,
    )

    response.delete_cookie(
        key="notion_oauth_state",
        path="/",
    )

    response.delete_cookie(
        key="notion_code_verifier",
        path="/",
    )

    return response


# ---------------------------------------------------------
# CONNECTION STATUS
# ---------------------------------------------------------

@router.get("/connection")
async def notion_connection(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
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


# ---------------------------------------------------------
# LIST MCP TOOLS
# ---------------------------------------------------------

@router.get("/tools")
async def list_notion_tools(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    integration = get_notion_integration(
        db=db,
        user_id=current_user.id,
    )

    if not integration:
        raise HTTPException(
            status_code=400,
            detail="Notion is not connected",
        )

    if not integration.connected:
        raise HTTPException(
            status_code=400,
            detail="Notion integration is disconnected",
        )

    client = NotionMCPClient(
        notion_token=integration.access_token
    )

    result = await client.list_tools()

    tools = []

    for tool in result.tools:

        if hasattr(tool, "model_dump"):
            tools.append(
                tool.model_dump()
            )

        else:
            tools.append(
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                }
            )

    return {
        "count": len(tools),
        "tools": tools,
    }

@router.get("/test-tool-access")
async def test_tool_access(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    integration = get_notion_integration(
        db=db,
        user_id=current_user.id,
    )

    if not integration:
        raise HTTPException(
            status_code=400,
            detail="Notion is not connected",
        )

    if not integration.connected:
        raise HTTPException(
            status_code=400,
            detail="Notion integration is disconnected",
        )

    client = NotionMCPClient(
        notion_token=integration.access_token
    )

    result = await client.call_tool(
        tool_name="notion-get-tool-access",
        arguments={}
    )

    if hasattr(result, "model_dump"):
        return result.model_dump()

    return {
        "result": str(result)
    }
@router.get("/test-search")
async def test_notion_search(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    integration = get_notion_integration(
        db=db,
        user_id=current_user.id,
    )

    if not integration:
        raise HTTPException(
            status_code=400,
            detail="Notion is not connected",
        )

    if not integration.connected:
        raise HTTPException(
            status_code=400,
            detail="Notion integration is disconnected",
        )

    client = NotionMCPClient(
        notion_token=integration.access_token
    )

    result = await client.call_tool(
        tool_name="notion-search",
        arguments={
            "query": "project"
        },
    )

    if hasattr(result, "model_dump"):
        return result.model_dump()

    return {
        "result": str(result)
    }