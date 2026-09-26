import asyncio
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.exceptions import McpError

import httpx


class NotionMCPClient:

    def __init__(self, notion_token: str):
        self.notion_token = notion_token
        self.url = "https://mcp.notion.com/mcp"

    async def _with_session(self, action):
        """
        Opens one MCP session, initializes it, then runs `action(session)`.
        Retries on transient MCPError (e.g. -32603) since the hosted
        server can hiccup independently of our token being valid.
        """

        last_error = None

        for attempt in range(2):  # 1 retry

            try:
                async with httpx.AsyncClient(
                    headers={
                        "Authorization": f"Bearer {self.notion_token}",
                        "User-Agent": "NuroFlow-MCP-Client/1.0",
                    }
                ) as http_client:

                    async with streamable_http_client(
                        self.url,
                        http_client=http_client
                    ) as (read_stream, write_stream):

                        async with ClientSession(
                            read_stream,
                            write_stream
                        ) as session:

                            await session.initialize()
                            return await action(session)

            except McpError as e:
                last_error = e
                if attempt == 0:
                    await asyncio.sleep(1.5)
                    continue
                raise

        raise last_error

    async def list_tools(self):
        return await self._with_session(
            lambda session: session.list_tools()
        )

    async def call_tool(self, tool_name: str, arguments: dict):
        return await self._with_session(
            lambda session: session.call_tool(tool_name, arguments)
        )