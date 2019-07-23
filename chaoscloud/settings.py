# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from chaoslib.types import Control, Settings

__all__ = ["set_settings", "get_endpoint_url", "disable_publishing",
           "enable_publishing", "disable_policies", "enable_policies",
           "is_feature_enabled"]


def set_settings(url: str, token: str, disable_tls_verify: bool,
                 default_org: Dict[str, str], settings: Settings):
    """
    Set the Chaos Toolkit Cloud related entries in the Chaos Toolkit settings.

    This essentially does two things:

    * It sets an entry in the `auths` section for the domain defined in the
      `url`
    * It sets a `chaosiq` block in the `controls` section with the appropriate
      values for this plugin
    """
    set_auth(settings, url, token)
    control = get_control(settings)
    set_default_org(settings, default_org)

    control.update({
        'features': {
            'publish': 'on',
            'policies': 'on',
        },
        'provider': {
            'type': 'python',
            'module': 'chaoscloud.controls',
            'arguments': {
                'url': url,
                'verify_tls': not disable_tls_verify,
                'organizations': get_orgs(settings)
            }
        }
    })


def disable_publishing(settings: Settings):
    control = get_control(settings)
    control.setdefault('features', {})['publish'] = "off"


def enable_publishing(settings: Settings):
    control = get_control(settings)
    control.setdefault('features', {})['publish'] = "on"


def disable_policies(settings: Settings):
    control = get_control(settings)
    control.setdefault('features', {})['policies'] = "off"


def enable_policies(settings: Settings):
    control = get_control(settings)
    control.setdefault('features', {})['policies'] = "on"


def get_endpoint_url(settings: Settings,
                     default='https://console.chaostoolkit.com') -> str:
    """
    Get the configured URL of the Chaos Toolkit endpoint.
    """
    return settings.get('controls', {}).\
        get('chaostoolkit-cloud', {}).\
        get('provider', {}).\
        get('arguments', {}).\
        get('url', default)


###############################################################################
# Internals
###############################################################################
def set_auth(settings: Settings, url: str, token: str):
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


def get_control(settings: Settings) -> Control:
    controls = settings.setdefault('controls', {})
    return controls.setdefault('chaostoolkit-cloud', {})


def get_orgs(settings: Settings) -> List[Dict[str, Any]]:
    provider = \
        settings['controls']['chaostoolkit-cloud'].setdefault('provider', {})
    args = provider.setdefault('arguments', {})
    return args.setdefault('organizations', [])


def get_default_org(settings: Settings) -> Optional[Dict[str, Any]]:
    orgs = get_orgs(settings)
    for org in orgs:
        if org['default']:
            return org


def set_default_org(settings: Settings, org: Dict[str, str]):
    orgs = get_orgs(settings)
    current_default_org = get_default_org(settings)
    if current_default_org:
        current_default_org['default'] = False

    for o in orgs:
        if o['id'] == org['id']:
            o['default'] = True
            o['name'] = org['name']
            break
    else:
        orgs.append({
            'id': org["id"],
            'name': org["name"],
            'default': True
        })


def verify_tls_certs(settings: Settings) -> bool:
    return settings.get('controls', {}).\
        get('chaostoolkit-cloud', {}).\
        get('provider', {}).\
        get('arguments', {}).\
        get('verify_tls', True)


def is_feature_enabled(settings: Settings, feature: str) -> bool:
    control = get_control(settings)
    features = control.get("features", {})
    return features.get(feature) != "off"