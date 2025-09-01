from fastmcp import FastMCP

from tools import register_tools


def create_app() -> FastMCP:
    mcp = FastMCP("Demo MCP Server")
    register_tools(mcp)
    return mcp


if __name__ == "__main__":
    app = create_app()
    app.run(transport="streamable-http", host="localhost", port=9000)
