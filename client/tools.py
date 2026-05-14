from langchain_mcp_adapters.client import MultiServerMCPClient


async def load_mcp_tools():
    """
    Connect to MCP servers and load tools.
    """

    client = MultiServerMCPClient(
        {
            
            # Weather/Search MCP Server
            "weather-server": {
                "command": "python",
                "args": ["server/weather_server.py"],
                "transport": "stdio",
            },

            # Memory MCP Server
            "memory-server": {
                "command": "python",
                "args": ["memory_server/server.py"],
                "transport": "stdio",
            }
        }
    )

    tools = await client.get_tools()

    return tools