import re
from typing import Tuple, Dict, Any, Optional

_INT_WEATHER = re.compile(r"\bweather\s+(?:in|at|for)\s+(?P<place>[A-Za-z][\w\s,.-]{1,60})", re.I)
_INT_NUMBERS = re.compile(r"\b(?:sum|summary|stats)\b.*?(?P<numbers>(?:-?\d+(?:\.\d+)?(?:\s*,\s*|-|\s+))+)", re.I)
_INT_SLUG = re.compile(r"\b(?:slugify|make\s+slug|slug)\b[:\s]*(?P<text>.+)$", re.I)


async def parse_intent(message: str) -> Tuple[Optional[str], Dict[str, Any]]:
    """
    Return (tool_name, arguments) or (None, {}).
    Supported:
      - "get_weather": "weather in Dhaka"
      - "summarize_numbers": "stats 1,2,3 -4 5.5"
      - "slugify_text": "slugify: Hello World!"
    """
    if not message or not isinstance(message, str):
        return None, {}

    # Weather by place
    m = _INT_WEATHER.search(message)
    if m:
        place = m.group("place").strip()
        return "get_weather", {"place": place}

    # Numbers summary
    m = _INT_NUMBERS.search(message)
    if m:
        raw = m.group("numbers")
        nums = re.findall(r"-?\d+(?:\.\d+)?", raw)
        numbers = [float(x) for x in nums]
        return "summarize_numbers", {"numbers": numbers}

    # Slugify
    m = _INT_SLUG.search(message)
    if m:
        text = m.group("text").strip()
        return "slugify_text", {"text": text}

    return None, {}
