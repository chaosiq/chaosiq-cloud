# -*- coding: utf-8 -*-
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from chaoslib.types import Control, Settings

__all__ = ["set_settings", "get_endpoint_url", "disable_publishing",
           "enable_publishing", "disable_safeguards", "enable_safeguards",
           "is_feature_enabled", "get_verify_tls", "get_auth_token"]


def set_settings(url: str, token: str, verify_tls: bool,
                 default_org: Dict[str, str], settings: Settings):
    """
    Set the ChaosIQ Cloud related entries in the Chaos Toolkit settings.

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
            'safeguards': 'on',
        },
        'provider': {
            'type': 'python',
            'module': 'chaoscloud.controls',
            'arguments': {
                'url': url,
                'verify_tls': verify_tls,
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


def disable_safeguards(settings: Settings):
    control = get_control(settings)
    control.setdefault('features', {})['safeguards'] = "off"


def enable_safeguards(settings: Settings):
    control = get_control(settings)
    control.setdefault('features', {})['safeguards'] = "on"


def get_endpoint_url(settings: Settings,
                     default='https://console.chaosiq.io') -> str:
    """
    Get the configured URL of the ChaosIQ endpoint.
    """
    return settings.get('controls', {}).\
        get('chaosiq-cloud', {}).\
        get('provider', {}).\
        get('arguments', {}).\
        get('url', default)


def get_verify_tls(settings: Settings) -> str:
    """
    Get the configured tls verify of the ChaosIQ endpoint.
    """
    return settings.get('controls', {}).\
        get('chaosiq-cloud', {}).\
        get('provider', {}).\
        get('arguments', {}).\
        get('verify_tls')


def get_auth_token(settings: Settings, url) -> str:
    if 'auths' not in settings:
        settings['auths'] = {}

    p = urlparse(url)
    for domain in settings['auths']:
        if domain == p.netloc:
            return settings['auths'].get(domain, {}).get("value")


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
    if not settings:
        return
    controls = settings.setdefault('controls', {})
    return controls.setdefault('chaosiq-cloud', {})


def get_orgs(settings: Settings) -> List[Dict[str, Any]]:
    provider = \
        settings['controls']['chaosiq-cloud'].setdefault('provider', {})
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
        get('chaosiq-cloud', {}).\
        get('provider', {}).\
        get('arguments', {}).\
        get('verify_tls', True)


def is_feature_enabled(settings: Settings, feature: str) -> bool:
    control = get_control(settings)
    if not control:
        return False
    features = control.get("features", {})
    return features.get(feature) != "off"
