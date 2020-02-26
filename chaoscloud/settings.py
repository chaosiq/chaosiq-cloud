# -*- coding: utf-8 -*-
from copy import deepcopy
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from chaoslib.types import Control, Settings

__all__ = ["set_settings", "get_endpoint_url",
           "is_feature_enabled", "get_verify_tls", "get_auth_token",
           "enable_feature", "disable_feature", "FEATURES",
           "has_chaosiq_extension_configured"]


FEATURES = ['publish', 'safeguards', 'workspace']


def set_settings(url: str, token: str, verify_tls: bool,
                 default_org: Dict[str, str], default_team: Dict[str, str],
                 settings: Settings):
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
    default_org = deepcopy(default_org)
    set_default_team(default_org, default_team)
    set_default_org(settings, default_org)

    features = control.setdefault('features', {})
    for feature in FEATURES:
        features.setdefault(feature, 'on')

    control.update({
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


def disable_feature(settings: Settings, feature: str):
    if feature not in FEATURES:
        return

    control = get_control(settings)
    if not control:
        return

    control.setdefault('features', {})[feature] = "off"


def enable_feature(settings: Settings, feature: str):
    if feature not in FEATURES:
        return

    control = get_control(settings)
    if not control:
        return

    control.setdefault('features', {})[feature] = "on"


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


def has_chaosiq_extension_configured(settings: Settings) -> bool:
    """
    Lookup for the chaosiq control extension.
    """
    return settings.get('controls', {}).get('chaosiq-cloud') is not None


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


def get_teams(org: Dict[str, str]) -> List[Dict[str, Any]]:
    return org.setdefault('teams', [])


def get_default_team(org: Dict[str, str]) -> Optional[Dict[str, Any]]:
    teams = get_teams(org)
    for team in teams:
        if team['default']:
            return team


def set_default_org(settings: Settings, org: Dict[str, str]):
    orgs = get_orgs(settings)
    current_default_org = get_default_org(settings)
    if current_default_org:
        current_default_org['default'] = False

    for o in orgs:
        if o['id'] == org['id']:
            o['default'] = True
            o['name'] = org['name']
            o['teams'] = org["teams"]
            break
    else:
        orgs.append({
            'id': org["id"],
            'name': org["name"],
            'default': True,
            'teams': org["teams"]
        })


def set_default_team(org: Dict[str, str], team: Dict[str, str]):
    teams = get_teams(org)
    current_default_team = get_default_team(org)
    if current_default_team:
        current_default_team['default'] = False

    for t in teams:
        if t['id'] == team['id']:
            t['default'] = True
            t['name'] = team['name']
            break
    else:
        teams.append({
            'id': team["id"],
            'name': team["name"],
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
