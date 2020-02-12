__all__ = ['status_in_range', 'response_time_under',
           'response_time_above', 'status_must_be']


def status_must_be(value: int = None, expected: int = 200) -> bool:
    """
    Validates the status code of a HTTP call is as expected.
    """
    return value == expected


def status_in_range(value: int, lower: int = 100,
                    upper: int = 600) -> bool:
    """
    Validates the status code of a HTTP call is within the given boundary,
    inclusive.
    """
    return value in range(lower, upper+1)


def response_time_under(value: float = None, duration: float = 0) -> bool:
    """
    Validates the response time value of a HTTP call falls below the
    given duration in milliseconds.
    """
    return value <= duration


def response_time_above(value: float = None, duration: float = 0) -> bool:
    """
    Validates the response time value of a HTTP call is greater than the
    given duration in milliseconds.
    """
    return value >= duration
