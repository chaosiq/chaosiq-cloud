# -*- coding: utf-8 -*-
from logzero import logger
import requests

__all__ = ["request_teams", "request_team"]


def request_teams(teams_url: str, token: str,
                  verify_tls: bool = True) -> requests.Response:
    try:
        return requests.get(teams_url, headers={
                "Authorization": "Bearer {}".format(token)
            }, verify=verify_tls)
    except requests.exceptions.SSLError as x:
        logger.error(
            "Failed to communicate over TLS with the ChaosIQ endpoint: "
            "{}".format(str(x)))


def request_team(team_url: str, token: str,
                 verify_tls: bool = True) -> requests.Response:
    try:
        return requests.get(team_url, headers={
                "Authorization": "Bearer {}".format(token)
            }, verify=verify_tls)
    except requests.exceptions.SSLError as x:
        logger.error(
            "Failed to communicate over TLS with the ChaosIQ endpoint: "
            "{}".format(str(x)))
