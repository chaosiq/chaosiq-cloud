# -*- coding: utf-8 -*-

import requests

__all__ = ["verify_ssl_certificate"]


def verify_ssl_certificate(url, token):
    return requests.head(url, headers={
        "Authorization": "Bearer {}".format(token)
    })
