from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client
from mcp.shared.exceptions import MCPError as McpError  # mcp>=2.0 renamed this class

import httpx


class NotionMCPClient:

    def __init__(self, notion_token: str):
        self.notion_token = notion_token
        self.url = "https://mcp.notion.com/mcp"

    async def list_tools(self):

        async with httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.notion_token}",
                "User-Agent": "NuroFlow-MCP-Client/1.0",
            }
        ) as http_client:

            async with streamable_http_client(
                self.url,
                http_client=http_client
            ) as (
                read_stream,
                write_stream
            ):

                async with ClientSession(
                    read_stream,
                    write_stream
                ) as session:

                    await session.initialize()

                    return await session.list_tools()

    async def call_tool(
        self,
        tool_name: str,
        arguments: dict,
    ):

        async with httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {self.notion_token}",
                "User-Agent": "NuroFlow-MCP-Client/1.0",
            }
        ) as http_client:

            async with streamable_http_client(
                self.url,
                http_client=http_client
            ) as (
                read_stream,
                write_stream
            ):

                async with ClientSession(
                    read_stream,
                    write_stream
                ) as session:

                    await session.initialize()

                    return await session.call_tool(
                        tool_name,
                        arguments,
                    )