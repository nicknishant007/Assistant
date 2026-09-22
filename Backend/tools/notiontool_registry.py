from tools.notion_tool import (
    notion_get_tool_access_tool,
    notion_search_tool,
    notion_fetch_tool,
    notion_create_pages_tool,
    notion_update_page_tool,
    notion_query_data_source_tool,
    notion_create_comment_tool,
    notion_get_comments_tool
)


TOOLS = {

    # ============================================================
    # 1. GET TOOL ACCESS
    # ============================================================

    "notion_get_tool_access": {

        "function": notion_get_tool_access_tool,

        "description":
        """
        Check which Notion MCP capabilities are currently
        available for the connected user's Notion workspace.

        This tool does not modify the workspace.

        Use it when the availability of a Notion capability
        is unknown or when a tool may have plan-specific
        restrictions.
        """,

        "use_when":
        """
        Use when:

        - Notion tool availability is unknown.
        - A workflow needs to check whether a restricted
          Notion operation is available.
        - The agent needs to inspect current tool restrictions.

        Usually this is a bootstrap operation and its result
        should be reused for the rest of the workflow.
        """,

        "prerequisite_tools": [],

        "input_parameters": {

            "tool_names":
                "list[str] (optional)"

        },

        "output": {

            "tool_access": "dict",

            "tool_status": {
                "status": "str",
                "restricted_parameters": "dict (optional)"
            }
        },

        "example_output":
        {
            "search": {
                "status": "available"
            },

            "fetch": {
                "status": "available"
            },

            "create_pages": {
                "status": "available"
            }
        }
    },


    # ============================================================
    # 2. SEARCH NOTION
    # ============================================================

    "notion_search": {

        "function": notion_search_tool,

        "description":
        """
        Search the user's Notion workspace for pages,
        projects, notes, databases, documents, or users.

        This is the primary Notion discovery tool.

        It should normally be used when the agent does not
        already know the exact Notion page ID or URL.
        """,

        "use_when":
        """
        Use when:

        - User asks to find a Notion page.
        - User mentions a project or note by name.
        - User asks to find a document.
        - User asks to find a database.
        - User refers to something in Notion without providing
          its page ID or URL.
        - A later workflow step requires a Notion page ID.
        - A later workflow step requires a Notion page URL.

        Examples:

        - "Find my NuroFlow notes."
        - "Find the project tracker."
        - "Find my meeting notes."
        - "Search for the AI project."
        """,

        "prerequisite_tools": [],

        "input_parameters": {

            "query": "str",

            "query_type":
                "str (optional: internal | user)",

            "data_source_url":
                "str (optional)",

            "page_url":
                "str (optional)",

            "teamspace_id":
                "str (optional)",

            "filters":
                "dict (optional)",

            "sort":
                "dict (optional)",

            "page_size":
                "int (optional)",

            "max_highlight_length":
                "int (optional)"
        },

        "output": {

            "results": [
                {
                    "id": "str",
                    "title": "str",
                    "url": "str (optional)",
                    "highlight": "str (optional)"
                }
            ],

            "type": "workspace_search"
        },

        "example_output":
        {
            "results": [
                {
                    "id": "abc123",
                    "title": "NuroFlow Architecture",
                    "url": "https://www.notion.so/...",
                    "highlight": "NuroFlow architecture..."
                }
            ],

            "type": "workspace_search"
        }
    },


    # ============================================================
    # 3. FETCH NOTION
    # ============================================================

    "notion_fetch": {

        "function": notion_fetch_tool,

        "description":
        """
        Fetch the complete information for a specific
        Notion page, database, data source, saved view,
        or supported Notion resource.

        This is the primary information retrieval tool
        after a page or database has been identified.
        """,

        "use_when":
        """
        Use when:

        - Search returned a page that must be inspected.
        - User asks to open/read a specific Notion page.
        - Page content is required for summarization.
        - Page content is required before modification.
        - Database schema is required.
        - Data source information is required.
        - Comments/discussions need to be located.
        - A Notion resource needs to be inspected.

        IMPORTANT:

        Before updating a page, fetch the page first.

        Before querying or creating pages inside a database,
        fetch the database first to obtain its schema and
        data source information.
        """,

        "prerequisite_tools": [],

        "input_parameters": {

            "id":
                "str",

            "include_transcript":
                "bool (optional)",

            "include_discussions":
                "bool (optional)"
        },

        "output": {

            "id": "str",

            "type":
                "page | database | data_source | view | resource",

            "content":
                "str",

            "properties":
                "dict (optional)",

            "data_sources":
                "list (optional)"
        },

        "example_output":
        {
            "id": "abc123",

            "type": "page",

            "content":
                "# NuroFlow Architecture\n\n..."

        }
    },


    # ============================================================
    # 4. CREATE PAGES
    # ============================================================

    "notion_create_pages": {

        "function": notion_create_pages_tool,

        "description":
        """
        Create one or more pages in the user's Notion workspace.

        Pages can be created as standalone pages, under a
        parent page, or inside a Notion data source/database.

        When the user clearly wants a durable page but does not
        specify a destination, draft mode should be preferred.
        """,

        "use_when":
        """
        Use when:

        - User asks to create a Notion page.
        - User asks to create notes.
        - User asks to create meeting notes.
        - User asks to create a project document.
        - User asks to add an item to a Notion database.
        - User wants information written into Notion.

        For database page creation:

        - Fetch the database first.
        - Inspect the data source schema.
        - Use the correct property names.
        - Include the required title property.

        When no destination is specified:

        - Prefer creation_mode='draft'.
        """,

        "prerequisite_tools": [],

        "input_parameters": {

            "pages":
                "list[dict]",

            "parent":
                "dict (optional)",

            "creation_mode":
                "str (optional: draft)",

            "allow_async":
                "bool (optional)"
        },

        "output": {

            "pages": [
                {
                    "page_id": "str",
                    "url": "str",
                    "title": "str"
                }
            ],

            "async_task":
                "dict (optional)"
        },

        "example_output":
        {
            "pages": [
                {
                    "page_id": "abc123",
                    "url":
                        "https://www.notion.so/...",
                    "title":
                        "Today's Meeting Notes"
                }
            ]
        }
    },


    # ============================================================
    # 5. UPDATE PAGE
    # ============================================================

    "notion_update_page": {

        "function": notion_update_page_tool,

        "description":
        """
        Update an existing Notion page's properties or content.

        This is the primary Notion modification tool.

        It supports:

        - Updating properties.
        - Updating selected content.
        - Inserting content.
        - Replacing page content.
        - Applying templates.
        - Updating verification state.

        The agent should prefer targeted updates over replacing
        an entire page.
        """,

        "use_when":
        """
        Use when:

        - User wants to edit a Notion page.
        - User wants to change a property.
        - User wants to change a task status.
        - User wants to update page content.
        - User wants to append information.
        - User wants to replace a specific piece of text.
        - User wants to apply a page template.

        IMPORTANT:

        Fetch the page before making an update when the
        current page content or database schema is unknown.

        For database pages:

        - Fetch first.
        - Inspect exact property names.
        - Then perform the update.

        Prefer:

        update_content
        over
        replace_content

        whenever a targeted edit is sufficient.
        """,

        "prerequisite_tools": [
            "notion_fetch"
        ],

        "input_parameters": {

            "page_id":
                "str",

            "command":
                "str",

            "properties":
                "dict (optional)",

            "content_updates":
                "list[dict] (optional)",

            "new_str":
                "str (optional)",

            "content":
                "str (optional)",

            "position":
                "str (optional)",

            "template_id":
                "str (optional)",

            "verification_status":
                "str (optional)",

            "verification_expiry_days":
                "int (optional)"
        },

        "output": {

            "success":
                "bool",

            "page_id":
                "str",

            "updated_page":
                "dict (optional)"
        },

        "example_output":
        {
            "success": True,

            "page_id": "abc123",

            "updated_page": {
                "title":
                    "NuroFlow Project",
                "status":
                    "Done"
            }
        }
    },


    # ============================================================
    # 6. QUERY DATA SOURCE
    # ============================================================

    "notion_query_data_source": {

        "function": notion_query_data_source_tool,

        "description":
        """
        Query a Notion database/data source.

        Supports:

        - SQL queries.
        - Structured rows mode.
        - Saved database view mode.

        This is the primary tool for retrieving structured
        records from Notion databases.
        """,

        "use_when":
        """
        Use when:

        - User asks for tasks from a Notion database.
        - User wants records matching a condition.
        - User asks for tasks with a particular status.
        - User asks for database rows.
        - User wants filtered database information.
        - User wants sorted records.
        - User asks for structured Notion data.

        Examples:

        - "Show my tasks that are In Progress."
        - "Find all high priority tasks."
        - "Show the projects completed this month."
        - "Get all tasks from my project database."

        IMPORTANT:

        Fetch the database/data source first when the schema
        or data source URL is not already known.
        """,

        "prerequisite_tools": [
            "notion_fetch"
        ],

        "input_parameters": {

            "data":
                "dict"
        },

        "output": {

            "rows": [
                "dict"
            ],

            "count":
                "int",

            "has_more":
                "bool (optional)",

            "next_cursor":
                "str (optional)"
        },

        "example_output":
        {
            "rows": [
                {
                    "Task":
                        "Implement MCP tools",

                    "Status":
                        "In Progress",

                    "Priority":
                        "High"
                },
                {
                    "Task":
                        "Build Notion agent",

                    "Status":
                        "In Progress",

                    "Priority":
                        "Medium"
                }
            ],

            "count": 2,

            "has_more": False
        }
    },


    # ============================================================
    # 7. CREATE COMMENT
    # ============================================================

    "notion_create_comment": {

        "function": notion_create_comment_tool,

        "description":
        """
        Add a comment to a Notion page or reply to an
        existing discussion.

        Supports:

        - Page-level comments.
        - Comments attached to selected content.
        - Replies to existing discussion threads.
        """,

        "use_when":
        """
        Use when:

        - User asks to comment on a Notion page.
        - User wants to leave feedback.
        - User wants to mention an issue on a page.
        - User wants to reply to an existing Notion discussion.
        - User wants to add context to a specific section.

        Use markdown for normal comments.

        Use discussion_id when replying to an existing
        discussion thread.
        """,

        "prerequisite_tools": [],

        "input_parameters": {

            "page_id":
                "str",

            "markdown":
                "str (optional)",

            "rich_text":
                "list[dict] (optional)",

            "discussion_id":
                "str (optional)",

            "selection_with_ellipsis":
                "str (optional)"
        },

        "output": {

            "success":
                "bool",

            "comment":
                "dict"
        },

        "example_output":
        {
            "success": True,

            "comment": {
                "page_id":
                    "abc123",

                "content":
                    "Deployment is ready."
            }
        }
    },


    # ============================================================
    # 8. GET COMMENTS
    # ============================================================

    "notion_get_comments": {

        "function": notion_get_comments_tool,

        "description":
        """
        Retrieve comments and discussion threads from
        a Notion page.

        Can retrieve page-level discussions, discussions
        on child blocks, resolved discussions, or a specific
        discussion thread.
        """,

        "use_when":
        """
        Use when:

        - User asks what people commented on a page.
        - User wants to read discussion threads.
        - User wants to inspect feedback.
        - User wants comments from child blocks.
        - User references an existing discussion thread.

        If discussion locations inside the page are required,
        fetch the page with include_discussions=true first.
        """,

        "prerequisite_tools": [],

        "input_parameters": {

            "page_id":
                "str",

            "include_resolved":
                "bool (optional)",

            "include_all_blocks":
                "bool (optional)",

            "discussion_id":
                "str (optional)"
        },

        "output": {

            "discussions": [
                {
                    "discussion_id":
                        "str",

                    "comments":
                        "list"
                }
            ]
        },

        "example_output":
        {
            "discussions": [
                {
                    "discussion_id":
                        "discussion://...",

                    "comments": [
                        {
                            "author":
                                "John",

                            "content":
                                "Looks good."
                        }
                    ]
                }
            ]
        }
    }
}


# ============================================================
# TOOL DESCRIPTION BUILDER
# ============================================================

def get_tool_descriptions():

    descriptions = []

    for name, info in TOOLS.items():

        descriptions.append(
            f"""
Tool: {name}

Description:
{info.get('description', '')}

Use When:
{info.get('use_when', '')}

Prerequisite Tools:
{info.get('prerequisite_tools', [])}

Input Parameters:
{info.get('input_parameters', {})}

Output:
{info.get('output', {})}
"""
        )

    return "\n".join(descriptions)