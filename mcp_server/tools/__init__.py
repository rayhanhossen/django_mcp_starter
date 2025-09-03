from fastmcp import FastMCP

from .numbers import summarize_numbers
from .text import slugify_text
from .weather import get_weather


def register_tools(mcp: FastMCP) -> None:
    """
    Register all tool functions with the given FastMCP instance.

    Keeping this logic here means your tools stay framework-agnostic
    and only this layer knows about FastMCP registration.
    """
    # you can register by calling the decorator as a function:
    mcp.tool(name="summarize_numbers")(summarize_numbers)
    mcp.tool(name="slugify_text")(slugify_text)
    mcp.tool(name="get_weather")(get_weather)
