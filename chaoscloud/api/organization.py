# -*- coding: utf-8 -*-
from logzero import logger
import requests

__all__ = ["request_orgs"]


def request_orgs(orgs_url: str, token: str,
                 verify_tls: bool = True) -> requests.Response:
    try:
        return requests.get(orgs_url, headers={
                "Authorization": "Bearer {}".format(token)
            }, verify=verify_tls)
    except requests.exceptions.SSLError as x:
        logger.error(
            "Failed to communicate over TLS with the ChaosIQ endpoint: "
            "{}".format(str(x)))
