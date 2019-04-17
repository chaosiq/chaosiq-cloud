# -*- coding: utf-8 -*-

from chaosiqctk import Context, get_context


def test_get_context_from_cli():
    context = get_context({}, "", {})

    assert context.experiment is None
    assert context.url is None
    assert context.token is None


def test_get_context_from_settings():
    context = get_context({}, "", {
        "vendor": {
            "chaosiq": {
                "token": "XYZ",
                "url": "https://chaosiq.io"
            }
        }
    })  

    assert context.experiment is None
    assert context.url == "https://chaosiq.io"
    assert context.token == "XYZ"


def test_get_context_cli_override_all():
    context = get_context({
        "extensions": [
            {
                "name": "chaosiq",
                "experiment": "1234"
            }
        ]
    }, 
    "",
    {
        "vendor": {
            "chaosiq": {
                "token": "XYZ",
                "url": "https://chaosiq.io"
            }
        }
    })

    assert context.experiment == "1234"
    assert context.url == "https://chaosiq.io"
    assert context.token == "XYZ"
