# -*- coding: utf-8 -*-
from urllib.parse import urlparse

from chaoslib.types import Settings

__all__ = ["set_settings"]


def set_settings(url: str, token: str, settings: Settings):
    """
    Set the ChaosIQ related entries in the Chaos Toolkit settings.
    """
    if 'auths' not in settings:
        settings['auths'] = {}

    p = urlparse(url)
    for domain in settings['auths']:
        if domain == p.netloc:
            auth = settings['auths'][domain]
            auth["type"] = "bearer"
            auth["value"] = token
            break
    else:
        auth = settings['auths'][p.netloc] = {}
        auth["type"] = "bearer"
        auth["value"] = token

    if 'vendor' not in settings:
        settings['vendor'] = {}

    vendors = settings['vendor']

    if 'chaosiq' not in vendors:
        vendors['chaosiq'] = {}

    vendors['chaosiq'].update({
        'url': url,
        'token': token
    })
