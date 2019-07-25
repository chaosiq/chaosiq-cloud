# -*- coding: utf-8 -*-

import requests

__all__ = ["request_orgs"]


def request_orgs(orgs_url, token, disable_tls_verify):
    return requests.get(orgs_url, headers={
            "Authorization": "Bearer {}".format(token)
        }, verify=not disable_tls_verify)
