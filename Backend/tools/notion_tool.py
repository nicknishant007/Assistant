from typing import Any

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

# 1. Get Notion Tool Access

async def notion_get_tool_access_tool(
    db,
    user_id: str,
    tool_names: list[str] | None = None,
):
    """
    Get the capabilities available for the user's
    Notion connection.
    """

    return await get_notion_tool_access(
        db=db,
        user_id=user_id,
        tool_names=tool_names,
    )


# 2. Search Notion

async def notion_search_tool(
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

    return await search_notion(
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


# 3. Fetch Notion

async def notion_fetch_tool(
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

    return await fetch_notion(
        db=db,
        user_id=user_id,
        id=id,
        include_transcript=include_transcript,
        include_discussions=include_discussions,
    )


# 4. Create Notion Pages

async def notion_create_pages_tool(
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

    return await create_notion_pages(
        db=db,
        user_id=user_id,
        pages=pages,
        parent=parent,
        creation_mode=creation_mode,
        allow_async=allow_async,
    )


# 5. Update Notion Page


async def notion_update_page_tool(
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

    return await update_notion_page(
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



# 6. Query Notion Data Source

async def notion_query_data_source_tool(
    db,
    user_id: str,
    data: dict[str, Any],
):
    """
    Query a Notion data source/database.
    """

    return await query_notion_data_source(
        db=db,
        user_id=user_id,
        data=data,
    )


# 7. Create Notion Comment

async def notion_create_comment_tool(
    db,
    user_id: str,
    page_id: str,
    markdown: str | None = None,
    rich_text: list[dict[str, Any]] | None = None,
    discussion_id: str | None = None,
    selection_with_ellipsis: str | None = None,
):
    """
    Create a new Notion comment or reply to an
    existing discussion.
    """

    return await create_notion_comment(
        db=db,
        user_id=user_id,
        page_id=page_id,
        markdown=markdown,
        rich_text=rich_text,
        discussion_id=discussion_id,
        selection_with_ellipsis=selection_with_ellipsis,
    )



# 8. Get Notion Comments

async def notion_get_comments_tool(
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

    return await get_notion_comments(
        db=db,
        user_id=user_id,
        page_id=page_id,
        include_resolved=include_resolved,
        include_all_blocks=include_all_blocks,
        discussion_id=discussion_id,
    )