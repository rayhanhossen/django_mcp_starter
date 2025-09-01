import re
from typing import Dict, Any

async def slugify_text(
    text: str,
    max_len: int = 60,
    lowercase: bool = True,
    keep_numbers: bool = True,
) -> Dict[str, Any]:
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
        s = re.sub(r"\s+", "-", s)          # spaces → dashes
        s = re.sub(r"-{2,}", "-", s)        # collapse dashes
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
