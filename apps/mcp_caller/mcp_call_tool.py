import os
import asyncio
from typing import Any, Dict, Optional
from fastmcp import Client

# Configure via env; override per-call if needed
MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://localhost:9000/mcp")


class MCPError(Exception):
    """Raised for MCP client/tool errors."""
    pass


async def call_mcp_tool(
        name: str,
        arguments: Dict[str, Any],
        *,
        timeout: float = 10.0,
        base_url: Optional[str] = None,
        do_ping: bool = True,
) -> Any:
    """
    Call an MCP tool asynchronously and return normalized data.

    Args:
        name: MCP tool name (e.g., "summarize_numbers").
        arguments: JSON-serializable dict of arguments.
        timeout: Overall timeout (seconds) for the tool call.
        base_url: Optional override for MCP server URL.
        do_ping: If True, ping the server first for quick health check.

    Returns:
        The tool's data payload (already normalized).

    Raises:
        MCPError: For validation, server, timeout, or tool-level errors.
    """
    if not isinstance(arguments, dict):
        raise MCPError("arguments must be a JSON object (dict)")

    url = base_url or MCP_BASE_URL
    client = Client(url)

    try:
        async with client:
            if do_ping:
                # keep ping budget modest so call still has time
                await asyncio.wait_for(client.ping(), timeout=min(2.0, timeout / 2))
            result = await asyncio.wait_for(
                client.call_tool(name=name, arguments=arguments),
                timeout=timeout,
            )
    except asyncio.TimeoutError as e:
        raise MCPError("MCP server timed out") from e
    except Exception as e:
        # Surface a concise, user-friendly message
        raise MCPError(str(e)) from e

    # Normalize typical fastmcp result structures
    data = getattr(result, "data", result)

    # If your tools follow {"response": False, "error": "..."} convention, handle it here
    if isinstance(data, dict) and data.get("response") is False:
        raise MCPError(data.get("error") or "Tool reported failure")

    return data
