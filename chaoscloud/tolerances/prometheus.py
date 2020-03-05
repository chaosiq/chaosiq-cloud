from typing import Any, Dict, Optional

__all__ = ["result_value_under", "result_value_above", "result_value_between"]


def result_value_under(value: Dict[str, Any] = None,
                       upper: float = 1.0) -> bool:
    """
    Validates the result value is lower or equal to the given upper bound.
    """
    value = extract_value(value)
    if value is None:
        return False
    return value <= upper


def result_value_above(value: float = None, lower: float = 0.0) -> bool:
    """
    Validates the result value is greater or equal to the given lower bound.
    """
    value = extract_value(value)
    if value is None:
        return False
    return value >= lower


def result_value_between(value: float = None, lower: float = 0,
                         upper: float = 1.0) -> bool:
    """
    Validates the result value is within the given range, inclusive.
    """
    value = extract_value(value)
    if value is None:
        return False
    return lower <= value <= upper


###############################################################################
# Internals
###############################################################################
def extract_value(result: Dict[str, Any]) -> Optional[float]:
    if not result:
        return

    result = result.get("data", {}).get("result", [])
    if not result:
        return

    value = result[0].get("value", [])
    if not value:
        return

    value = value[1]
    if value == "NaN":
        return

    return value
