import asyncio
import threading
from typing import Any, Callable

from services.notion.notion_service import (
    get_notion_tool_access,
    search_notion,
    fetch_notion,
    create_notion_pages,
    update_notion_page,
    query_notion_data_source,
    create_notion_comment,
    get_notion_comments,
)


# ============================================================
# ASYNC -> SYNC BRIDGE
# ============================================================

def _run_async(
    async_func: Callable[..., Any],
    **kwargs,
):
    """
    Execute an async function from synchronous code.

    - If there is no running event loop, use asyncio.run().
    - If a loop is already running (for example FastAPI),
      execute the coroutine in a separate thread.
    """

    try:
        asyncio.get_running_loop()

    except RuntimeError:
        # No running loop in this thread.
        return asyncio.run(
            async_func(**kwargs)
        )

    # A running event loop already exists in this thread.
    # We cannot call asyncio.run() directly here.
    result = {}
    error = {}

    def runner():
        try:
            result["value"] = asyncio.run(
                async_func(**kwargs)
            )

        except BaseException as exc:
            error["error"] = exc

    thread = threading.Thread(
        target=runner,
        daemon=True,
    )

    thread.start()
    thread.join()

    if "error" in error:
        raise error["error"]

    return result["value"]


# ============================================================
# 1. GET NOTION TOOL ACCESS
# ============================================================

def notion_get_tool_access_tool(
    db,
    user_id: str,
    tool_names: list[str] | None = None,
):
    """
    Get the capabilities available for the user's
    Notion connection.
    """

    return _run_async(
        get_notion_tool_access,
        db=db,
        user_id=user_id,
        tool_names=tool_names,
    )


# ============================================================
# 2. SEARCH NOTION
# ============================================================

def notion_search_tool(
    db,
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
    """
    Search the user's Notion workspace.
    """

    return _run_async(
        search_notion,
        db=db,
        user_id=user_id,
        query=query,
        query_type=query_type,
        data_source_url=data_source_url,
        page_url=page_url,
        teamspace_id=teamspace_id,
        filters=filters,
        sort=sort,
        page_size=page_size,
        max_highlight_length=max_highlight_length,
    )


# ============================================================
# 3. FETCH NOTION
# ============================================================

def notion_fetch_tool(
    db,
    user_id: str,
    id: str,
    include_transcript: bool | None = None,
    include_discussions: bool | None = None,
):
    """
    Fetch a Notion page, database, data source,
    view, or supported Notion resource.
    """

    return _run_async(
        fetch_notion,
        db=db,
        user_id=user_id,
        id=id,
        include_transcript=include_transcript,
        include_discussions=include_discussions,
    )


# ============================================================
# 4. CREATE NOTION PAGES
# ============================================================

def notion_create_pages_tool(
    db,
    user_id: str,
    pages: list[dict[str, Any]],
    parent: dict[str, Any] | None = None,
    creation_mode: str | None = None,
    allow_async: bool | None = None,
):
    """
    Create one or more Notion pages.
    """

    return _run_async(
        create_notion_pages,
        db=db,
        user_id=user_id,
        pages=pages,
        parent=parent,
        creation_mode=creation_mode,
        allow_async=allow_async,
    )


# ============================================================
# 5. UPDATE NOTION PAGE
# ============================================================

def notion_update_page_tool(
    db,
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
    """
    Update Notion page properties or content.
    """

    return _run_async(
        update_notion_page,
        db=db,
        user_id=user_id,
        page_id=page_id,
        command=command,
        properties=properties,
        new_str=new_str,
        content=content,
        content_updates=content_updates,
        position=position,
        template_id=template_id,
        verification_status=verification_status,
        verification_expiry_days=verification_expiry_days,
    )


# ============================================================
# 6. QUERY NOTION DATA SOURCE
# ============================================================

def notion_query_data_source_tool(
    db,
    user_id: str,
    data: dict[str, Any],
):
    """
    Query a Notion data source/database.
    """

    return _run_async(
        query_notion_data_source,
        db=db,
        user_id=user_id,
        data=data,
    )


# ============================================================
# 7. CREATE NOTION COMMENT
# ============================================================

def notion_create_comment_tool(
    db,
    user_id: str,
    page_id: str,
    markdown: str | None = None,
    rich_text: list[dict[str, Any]] | None = None,
    discussion_id: str | None = None,
    selection_with_ellipsis: str | None = None,
):
    """
    Create a new Notion comment or reply to
    an existing discussion.
    """

    return _run_async(
        create_notion_comment,
        db=db,
        user_id=user_id,
        page_id=page_id,
        markdown=markdown,
        rich_text=rich_text,
        discussion_id=discussion_id,
        selection_with_ellipsis=selection_with_ellipsis,
    )


# ============================================================
# 8. GET NOTION COMMENTS
# ============================================================

def notion_get_comments_tool(
    db,
    user_id: str,
    page_id: str,
    include_resolved: bool = False,
    include_all_blocks: bool = False,
    discussion_id: str | None = None,
):
    """
    Get comments/discussions from a Notion page.
    """

    return _run_async(
        get_notion_comments,
        db=db,
        user_id=user_id,
        page_id=page_id,
        include_resolved=include_resolved,
        include_all_blocks=include_all_blocks,
        discussion_id=discussion_id,
    )