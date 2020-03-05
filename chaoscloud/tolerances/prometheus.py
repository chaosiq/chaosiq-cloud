from typing import Any, Dict, List

__all__ = ["result_value_under", "result_value_above", "result_value_between"]


def result_value_under(value: Dict[str, Any] = None,
                       upper: float = 1.0) -> bool:
    """
    Validates the result value is lower or equal to the given upper bound.
    """
    values = extract_values(value)
    if not value:
        return False

    if "NaN" in values:
        return False

    for v in values:
        if v == "Inf":
            return False
        if v == "-Inf":
            continue
        if float(v) > upper:
            return False

    return True


def result_value_above(value: float = None, lower: float = 0.0) -> bool:
    """
    Validates the result value is greater or equal to the given lower bound.
    """
    values = extract_values(value)
    if not value:
        return False

    if "NaN" in values:
        return False

    for v in values:
        if v == "-Inf":
            return False
        if v == "Inf":
            continue
        if float(v) < lower:
            return False

    return True


def result_value_between(value: float = None, lower: float = 0,
                         upper: float = 1.0) -> bool:
    """
    Validates the result value is within the given range, inclusive.
    """
    values = extract_values(value)
    if not value:
        return False

    if "NaN" in values:
        return False

    for v in values:
        if v == "-Inf":
            return False
        if v == "Inf":
            return False
        if float(v) < lower:
            return False
        if float(v) > upper:
            return False

    return True


###############################################################################
# Internals
###############################################################################
def extract_values(result: Dict[str, Any]) -> List[str]:  # noqa: C901
    if not result:
        return []

    if result.get("status") != "success":
        return []

    data = result.get("data", {})
    if not data:
        return []

    result_type = data.get("resultType")
    results = data.get("result")

    values = []
    if result_type == "vector":
        for item in results:
            # instant vector
            if "value" in item:
                value = item.get("value", [])
                if value:
                    values.append(value[1])

            # range vector
            elif "values" in item:
                value = item.get("values", [])
                if value:
                    values.extend([v[1] for v in value])
    elif result_type == "scalar":
        values.append(results[1])
    elif result_type == "string":
        values.append(results[1])

    return values
