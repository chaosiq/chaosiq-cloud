# -*- coding: utf-8 -*-
import requests

__all__ = ["request_orgs"]


def request_orgs(orgs_url: str, token: str,
                 verify_tls: bool = True) -> requests.Response:
    return requests.get(orgs_url, headers={
            "Authorization": "Bearer {}".format(token)
        }, verify=verify_tls)
