# -*- coding: utf-8 -*-
import requests

__all__ = ["request_orgs"]


def request_orgs(orgs_url, token, disable_tls_verify) -> requests.Response:
    return requests.get(orgs_url, headers={
            "Authorization": "Bearer {}".format(token)
        }, verify=disable_tls_verify)
