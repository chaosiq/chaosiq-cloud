# -*- coding: utf-8 -*-
from chaoscloud.settings import get_endpoint_url, set_settings


def test_adding_new_chaosiq_settings(default_org, default_team):
    settings = {}
    hub_url = "https://myhub.com:9090/"
    token = "mytoken"
    set_settings(hub_url, token, False, default_org, default_team, settings)
    assert 'auths' in settings
    assert 'myhub.com:9090' in settings['auths']
    assert settings['auths']['myhub.com:9090']['type'] == 'bearer'
    assert settings['auths']['myhub.com:9090']['value'] == token

    assert 'controls' in settings
    assert 'chaosiq-cloud' in settings['controls']

    assert 'provider' in settings['controls']['chaosiq-cloud']
    provider = settings['controls']['chaosiq-cloud']['provider']
    assert 'type' in provider
    assert 'module' in provider
    assert provider['type'] == 'python'
    assert provider['module'] == 'chaoscloud.controls'

    assert 'arguments' in provider
    args = provider['arguments']
    assert 'url' in args
    assert args['url'] == hub_url
    assert 'verify_tls' in args
    assert args['verify_tls'] is False


def test_updating_existing_chaosiq_settings(default_org, default_team):
    hub_url = "https://myotherhub.com:9080/"
    token = "mytoken"
    settings = {
        'controls': {
            'chaosiq-cloud': {
                'provider': {
                    'type': 'python',
                    'module': 'chaoscloud.controls',
                    'arguments': {
                        'url': hub_url,
                        'verify_tls': False
                    }
                }
            }
        }
    }
    set_settings(
        hub_url, token, True, default_org, default_team, settings=settings)
    assert 'auths' in settings
    assert 'myotherhub.com:9080' in settings['auths']
    assert settings['auths']['myotherhub.com:9080']['type'] == 'bearer'
    assert settings['auths']['myotherhub.com:9080']['value'] == token

    assert 'controls' in settings
    assert 'chaosiq-cloud' in settings['controls']

    assert 'provider' in settings['controls']['chaosiq-cloud']
    provider = settings['controls']['chaosiq-cloud']['provider']
    assert 'type' in provider
    assert 'module' in provider
    assert provider['type'] == 'python'
    assert provider['module'] == 'chaoscloud.controls'

    assert 'arguments' in provider
    args = provider['arguments']
    assert 'url' in args
    assert args['url'] == hub_url
    assert 'verify_tls' in args
    assert args['verify_tls'] is True


def test_update_auth_token(default_org, default_team):
    hub_url = "https://myotherhub.com:9080/"
    token = "mytoken"
    settings = {
        'auths': {
            'myotherhub.com:9080': {
                'type': 'digest',
                'value': 'whatever'
            }
        },
        'controls': {
            'chaosiq-cloud': {
                'provider': {
                    'type': 'python',
                    'module': 'chaoscloud.controls',
                    'arguments': {
                        'url': hub_url,
                        'verify_tls': False
                    }
                }
            }
        }
    }
    set_settings(
        hub_url, token, False, default_org, default_team, settings=settings)
    assert 'auths' in settings
    assert 'myotherhub.com:9080' in settings['auths']
    assert settings['auths']['myotherhub.com:9080']['type'] == 'bearer'
    assert settings['auths']['myotherhub.com:9080']['value'] == token


def test_get_endpoint_url():
    hub_url = "https://myotherhub.com:9080/"
    settings = {
        'auths': {
            'myotherhub.com:9080': {
                'type': 'digest',
                'value': 'whatever'
            }
        },
        'controls': {
            'chaosiq-cloud': {
                'provider': {
                    'type': 'python',
                    'module': 'chaoscloud.controls',
                    'arguments': {
                        'url': hub_url,
                        'verify_tls': False
                    }
                }
            }
        }
    }
    assert get_endpoint_url(settings) == hub_url


def test_get_default_when_none_found():
    settings = {
        'auths': {
            'myotherhub.com:9080': {
                'type': 'digest',
                'value': 'whatever'
            }
        },
        'controls': {
            'chaosiq-cloud': {
                'provider': {
                    'type': 'python',
                    'module': 'chaoscloud.controls',
                    'arguments': {
                        'verify_tls': False
                    }
                }
            }
        }
    }
    assert get_endpoint_url(settings) == 'https://console.chaosiq.io'
