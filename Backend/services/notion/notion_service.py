from __future__ import annotations
from datetime import datetime,timedelta,UTC
from typing import Any
from sqlalchemy.orm import Session
from services.integration_service import (
    get_notion_integration,
    create_or_update_integration,
)
from .mcp_client import NotionMCPClient
from .oauth import discover_mcp_oauth, refresh_access_token

# Helpers

async def _get_notion_client(
    db: Session,
    user_id: str,
) -> NotionMCPClient:

    integration = get_notion_integration(
        db=db,
        user_id=user_id,
    )

    if not integration:
        raise ValueError("Notion is not connected for this user.")

    if not integration.connected:
        raise ValueError("Notion integration is disconnected.")

    if not integration.access_token:
        raise ValueError("Notion access token is missing.")

    # --- NEW: refresh if expired ---
    is_expired = (
        integration.token_expires_at is not None
        and integration.token_expires_at <= datetime.utcnow()
    )

    if is_expired:

        if not integration.refresh_token or not integration.notion_client_id:
            raise ValueError(
                "Notion token expired and cannot be refreshed "
                "(missing refresh_token or client_id). "
                "Please reconnect Notion."
            )

        metadata = await discover_mcp_oauth()

        tokens = await refresh_access_token(
            metadata=metadata,
            refresh_token=integration.refresh_token,
            client_id=integration.notion_client_id,
        )

        new_access_token = tokens.get("access_token")
        new_refresh_token = tokens.get("refresh_token") or integration.refresh_token

        expires_in = tokens.get("expires_in")
        new_expires_at = (
            datetime.now(UTC) + timedelta(seconds=int(expires_in))
            if expires_in is not None
            else None
        )

        integration = create_or_update_integration(
            db=db,
            user_id=user_id,
            provider="notion",
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            client_id=integration.notion_client_id,
            expires_at=new_expires_at,
        )

    return NotionMCPClient(
        notion_token=integration.access_token
    )
def _serialize_result(result: Any) -> Any:
    
    structured_content = getattr(
        result,
        "structuredContent",
        None,
    )

    if structured_content is not None:
        return structured_content

    content = getattr(
        result,
        "content",
        None,
    )

    if not content:
        return None

    text_parts = []

    for item in content:

        item_type = getattr(
            item,
            "type",
            None,
        )

        if item_type == "text":

            text_value = getattr(
                item,
                "text",
                None,
            )

            if text_value:
                text_parts.append(
                    text_value
                )

    if len(text_parts) == 1:
        return text_parts[0]

    return text_parts


def _check_mcp_error(result: Any) -> None:

    is_error = getattr(
        result,
        "isError",
        False,
    )

    if not is_error:
        return

    content = getattr(
        result,
        "content",
        None,
    ) or []

    messages = []

    for item in content:

        if getattr(item, "type", None) == "text":

            text = getattr(
                item,
                "text",
                None,
            )

            if text:
                messages.append(text)

    error_message = (
        "\n".join(messages)
        or "Notion MCP tool execution failed."
    )

    raise RuntimeError(
        error_message
    )


# 1. Get Notion Tool Access

async def get_notion_tool_access(
    db: Session,
    user_id: str,
    tool_names: list[str] | None = None,
):

    client = _get_notion_client(
        db=db,
        user_id=user_id,
    )

    arguments = {}

    if tool_names is not None:
        arguments["tool_names"] = tool_names

    result = await client.call_tool(
        "notion-get-tool-access",
        arguments,
    )

    _check_mcp_error(result)

    return _serialize_result(result)



# 2. Search Notion


async def search_notion(
    db: Session,
    user_id: str,
    query: str,
    query_type: str | None = None,
    data_source_url: str | None = None,
    page_url: str | None = None,
    teamspace_id: str | None = None,
    filters: dict[str, Any] | None = None,
    sort: dict[str, Any] | None = None,
    page_size: int = 10,
    max_highlight_length: int = 200,
):

    client = await _get_notion_client(
        db=db,
        user_id=user_id,
    )

    arguments: dict[str, Any] = {
        "query": query,
        "page_size": page_size,
        "max_highlight_length": max_highlight_length,
    }

    if query_type is not None:
        arguments["query_type"] = query_type

    if data_source_url is not None:
        arguments["data_source_url"] = data_source_url

    if page_url is not None:
        arguments["page_url"] = page_url

    if teamspace_id is not None:
        arguments["teamspace_id"] = teamspace_id

    if filters is not None:
        arguments["filters"] = filters

    if sort is not None:
        arguments["sort"] = sort

    result = await client.call_tool(
        "notion-search",
        arguments,
    )

    _check_mcp_error(result)

    return _serialize_result(result)


# 3. Fetch Notion Page / Database / Data Source


async def fetch_notion(
    db: Session,
    user_id: str,
    id: str,
    include_transcript: bool | None = None,
    include_discussions: bool | None = None,
):

    client = _get_notion_client(
        db=db,
        user_id=user_id,
    )

    arguments: dict[str, Any] = {
        "id": id,
    }

    if include_transcript is not None:
        arguments["include_transcript"] = (
            include_transcript
        )

    if include_discussions is not None:
        arguments["include_discussions"] = (
            include_discussions
        )

    result = await client.call_tool(
        "notion-fetch",
        arguments,
    )

    _check_mcp_error(result)

    return _serialize_result(result)


# 4. Create Pages


async def create_notion_pages(
    db: Session,
    user_id: str,
    pages: list[dict[str, Any]],
    parent: dict[str, Any] | None = None,
    creation_mode: str | None = None,
    allow_async: bool | None = None,
):

    client = _get_notion_client(
        db=db,
        user_id=user_id,
    )

    arguments: dict[str, Any] = {
        "pages": pages,
    }

    if parent is not None:
        arguments["parent"] = parent

    if creation_mode is not None:
        arguments["creation_mode"] = creation_mode

    if allow_async is not None:
        arguments["allow_async"] = allow_async

    result = await client.call_tool(
        "notion-create-pages",
        arguments,
    )

    _check_mcp_error(result)

    return _serialize_result(result)


# 5. Update Page

async def update_notion_page(
    db: Session,
    user_id: str,
    page_id: str,
    command: str,
    properties: dict[str, Any] | None = None,
    new_str: str | None = None,
    content: str | None = None,
    content_updates: list[dict[str, Any]] | None = None,
    position: str | None = None,
    template_id: str | None = None,
    verification_status: str | None = None,
    verification_expiry_days: int | None = None,
):

    client = _get_notion_client(
        db=db,
        user_id=user_id,
    )

    arguments: dict[str, Any] = {
        "page_id": page_id,
        "command": command,
    }

    if properties is not None:
        arguments["properties"] = properties

    if new_str is not None:
        arguments["new_str"] = new_str

    if content is not None:
        arguments["content"] = content

    if content_updates is not None:
        arguments["content_updates"] = (
            content_updates
        )

    if position is not None:
        arguments["position"] = position

    if template_id is not None:
        arguments["template_id"] = template_id

    if verification_status is not None:
        arguments["verification_status"] = (
            verification_status
        )

    if verification_expiry_days is not None:
        arguments["verification_expiry_days"] = (
            verification_expiry_days
        )

    result = await client.call_tool(
        "notion-update-page",
        arguments,
    )

    _check_mcp_error(result)

    return _serialize_result(result)


# 6. Query Data Source

async def query_notion_data_source(
    db: Session,
    user_id: str,
    data: dict[str, Any],
):

    client = _get_notion_client(
        db=db,
        user_id=user_id,
    )

    result = await client.call_tool(
        "notion-query-data-sources",
        {
            "data": data,
        },
    )

    _check_mcp_error(result)

    return _serialize_result(result)



# 7. Create Comment


async def create_notion_comment(
    db: Session,
    user_id: str,
    page_id: str,
    markdown: str | None = None,
    rich_text: list[dict[str, Any]] | None = None,
    discussion_id: str | None = None,
    selection_with_ellipsis: str | None = None,
):

    client = _get_notion_client(
        db=db,
        user_id=user_id,
    )

    arguments: dict[str, Any] = {
        "page_id": page_id,
    }

    if markdown is not None:
        arguments["markdown"] = markdown

    if rich_text is not None:
        arguments["rich_text"] = rich_text

    if discussion_id is not None:
        arguments["discussion_id"] = discussion_id

    if selection_with_ellipsis is not None:
        arguments["selection_with_ellipsis"] = (
            selection_with_ellipsis
        )

    result = await client.call_tool(
        "notion-create-comment",
        arguments,
    )

    _check_mcp_error(result)

    return _serialize_result(result)


# 8. Get Comments

async def get_notion_comments(
    db: Session,
    user_id: str,
    page_id: str,
    include_resolved: bool = False,
    include_all_blocks: bool = False,
    discussion_id: str | None = None,
):

    client = _get_notion_client(
        db=db,
        user_id=user_id,
    )

    arguments: dict[str, Any] = {
        "page_id": page_id,
        "include_resolved": include_resolved,
        "include_all_blocks": include_all_blocks,
    }

    if discussion_id is not None:
        arguments["discussion_id"] = (
            discussion_id
        )

    result = await client.call_tool(
        "notion-get-comments",
        arguments,
    )

    _check_mcp_error(result)

    return _serialize_result(result)