from typing import List
import re
from fastmcp import FastMCP

mcp = FastMCP("Demo MCP Server")


@mcp.tool
async def summarize_numbers(numbers: List[float]) -> dict:
    """
    Compute simple statistics over a list of numbers.

    Args:
        numbers: A list of floats (can be empty).

    Returns:
        JSON object with count, total, mean, minimum, maximum or errors.
    """
    try:
        if not isinstance(numbers, list) or not all(isinstance(x, (int, float)) for x in numbers):
            raise TypeError("Numbers must be a list of int/float")

        if not numbers:
            stats = {"count": 0, "total": 0.0, "mean": 0.0, "minimum": 0.0, "maximum": 0.0}
        else:
            total = float(sum(numbers))
            cnt = len(numbers)
            stats = {
                "count": cnt,
                "total": total,
                "mean": total / cnt,
                "minimum": float(min(numbers)),
                "maximum": float(max(numbers)),
            }

        return {"response": True, "data": stats}
    except Exception as e:
        return {"response": False, "error": f"Summarize_numbers failed: {e}"}


@mcp.tool
def slugify_text(
    text: str,
    max_len: int = 60,
    lowercase: bool = True,
    keep_numbers: bool = True,
) -> dict:
    """
    Convert text into a URL-friendly slug.

    Args:
        text: Source string.
        max_len: Max length for the slug (characters).
        lowercase: Lowercase the output.
        keep_numbers: Keep numeric characters (0-9).

    Returns:
        JSON object with slug, original_length, truncated flag or errors.
    """
    try:
        if text is None:
            raise ValueError("Text is required")
        if not isinstance(max_len, int) or max_len <= 0:
            raise ValueError("Max length must be a positive integer")

        s = text.strip()
        if lowercase:
            s = s.lower()

        allowed = r"a-z0-9" if keep_numbers else r"a-z"
        s = re.sub(fr"[^{allowed}\s-]", "", s)
        s = re.sub(r"\s+", "-", s)  # spaces → dashes
        s = re.sub(r"-{2,}", "-", s)  # collapse dashes
        s = s.strip("-")

        truncated = False
        if len(s) > max_len:
            s = s[:max_len].rstrip("-")
            truncated = True

        return {
            "response": True,
            "data": {
                "slug": s or "",
                "original_length": len(text),
                "truncated_flag": truncated,
            },
        }
    except Exception as e:
        return {"response": False, "error": f"Slugify text failed: {e}"}

if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="localhost", port=9000)