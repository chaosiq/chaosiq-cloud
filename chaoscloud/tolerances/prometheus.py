__all__ = ["result_value_under", "result_value_above", "result_value_between"]


def result_value_under(value: float = None, upper: float = 1.0) -> bool:
    """
    Validates the result value is lower or equal to the given upper bound.
    """
    return value <= upper


def result_value_above(value: float = None, lower: float = 0.0) -> bool:
    """
    Validates the result value is greater or equal to the given lower bound.
    """
    return value >= lower


def result_value_between(value: float = None, lower: float = 0,
                         upper: float = 1.0) -> bool:
    """
    Validates the result value is within the given range, inclusive.
    """
    return lower <= value <= upper
