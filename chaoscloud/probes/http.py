from datetime import datetime, timedelta
from typing import Any, Dict

from chaoslib.exceptions import ActivityFailed
from logzero import logger
import requests
from requests.exceptions import RequestException

__all__ = ["read_http_status_code", "time_http_call"]


def read_http_status_code(url: str, headers: Dict[str, Any] = None,
                          method: str = "GET", params: Dict[str, Any] = None,
                          json: Any = None, verify_tls: bool = True,
                          timeout: float = 30.0) -> int:
    """
    Perform a HTTP call and return its status code.
    """
    try:
        r = requests.request(
            method=method, url=url, params=params, json=json, headers=headers,
            verify=verify_tls)
        return r.status_code
    except RequestException:
        logger.debug("Failed to call url: {}".format(url), exc_info=True)
        raise ActivityFailed("Failed to request {}".format(url))


def time_http_call(url: str, headers: Dict[str, Any] = None,
                   method: str = "GET", params: Dict[str, Any] = None,
                   json: Any = None, verify_tls: bool = True,
                   timeout: float = 30.0) -> float:
    """
    Perform a HTTP call and return the time taken for the full request/response
    in milliseconds (decimal with microseconds).
    """
    try:
        now = datetime.now()
        requests.request(
            method=method, url=url, params=params, json=json, headers=headers,
            verify=verify_tls, timeout=timeout)
        return (datetime.now() - now) / timedelta(milliseconds=1)
    except RequestException:
        logger.debug("Failed to time url: {}".format(url), exc_info=True)
        raise ActivityFailed("Failed to time request {}".format(url))
