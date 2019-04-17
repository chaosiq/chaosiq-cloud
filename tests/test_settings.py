# -*- coding: utf-8 -*-

from chaosiqctk.settings import set_settings

def test_adding_new_chaosiq_settings():
    settings = {}
    hub_url = "myhub"
    token = "mytoken"
    set_settings(hub_url,token, settings)
    assert 'vendor' in settings
    assert 'chaosiq' in settings['vendor']
    assert 'url' in settings['vendor']['chaosiq']
    assert 'token' in settings['vendor']['chaosiq']
    assert settings['vendor']['chaosiq']['url'] == hub_url
    assert settings['vendor']['chaosiq']['token'] == token


def test_updating_existing_chaosiq_settings():
    settings = {'vendor': {
        'chaosiq': {
            'hub_url':'old-hub-url',
            'token':'old-token'
        }
    }}
    hub_url = "myhub"
    token = "mytoken"
    set_settings(hub_url,token, settings)
    assert 'vendor' in settings
    assert 'chaosiq' in settings['vendor']
    assert 'url' in settings['vendor']['chaosiq']
    assert 'token' in settings['vendor']['chaosiq']
    assert settings['vendor']['chaosiq']['url'] == hub_url
    assert settings['vendor']['chaosiq']['token'] == token


def test_only_updating_existing_chaosiq_settings():
    settings = {'vendor': {
        'chaosiq': {
            'url':'old-hub-url',
            'token':'old-token',
            'misc':'misc-setting'
        }
    }}
    hub_url = "myhub"
    token = "mytoken"
    set_settings(hub_url,token, settings)
    assert 'vendor' in settings
    assert 'chaosiq' in settings['vendor']
    assert 'url' in settings['vendor']['chaosiq']
    assert 'token' in settings['vendor']['chaosiq']
    assert settings['vendor']['chaosiq']['url'] == hub_url
    assert settings['vendor']['chaosiq']['token'] == token
    assert settings['vendor']['chaosiq']['misc'] == 'misc-setting'