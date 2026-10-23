from __future__ import annotations

import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main() -> None:
    async with streamable_http_client("http://127.0.0.1:8001/mcp") as (read_stream, write_stream, _):
        async with ClientSession(read_stream, write_stream) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            result = await session.call_tool("propose_safe_action", {"request": "Handle the delivery safely."})

    print(f"MCP protocol: {initialized.protocolVersion}")
    print("Available tools:", ", ".join(tool.name for tool in tools.tools))
    if result.isError:
        raise RuntimeError("The MCP tool call returned an error.")
    for item in result.content:
        if hasattr(item, "text"):
            print(item.text)


if __name__ == "__main__":
    asyncio.run(main())
