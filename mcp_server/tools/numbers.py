from typing import List, Dict, Any


async def summarize_numbers(numbers: List[float]) -> Dict[str, Any]:
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
