from fastmcp import FastMCP

# import tool functions
from .numbers import summarize_numbers
from .text import slugify_text


def register_tools(mcp: FastMCP) -> None:
    """
    Register all tool functions with the given FastMCP instance.

    Keeping this logic here means your tools stay framework-agnostic
    and only this layer knows about FastMCP registration.
    """
    # you can register by calling the decorator as a function:
    mcp.tool(name="summarize_numbers")(summarize_numbers)
    mcp.tool(name="slugify_text")(slugify_text)
