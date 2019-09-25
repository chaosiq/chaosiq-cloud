from chaoscloud.api import client_session

ENDPOINT = "https://console.chaosiq.io"


def test_do_not_set_auths_when_none_found_in_settings(organizations):
    with client_session(url=ENDPOINT, organizations=organizations) as s:
        assert "Authorization" not in s.headers


def test_set_authorization_from_settings(organizations):
    settings = {
        "auths": {
            "console.chaosiq.io": {
                "type": "digest",
                "value": "blah"
            }
        }
    }
    with client_session(url=ENDPOINT, organizations=organizations,
                        settings=settings) as s:
        assert "Authorization" in s.headers
        assert s.headers["Authorization"] == 'Digest blah'


def test_set_bearer_type_by_default_on_authorization(organizations):
    settings = {
        "auths": {
            "console.chaosiq.io": {
                "value": "blah"
            }
        }
    }
    with client_session(url=ENDPOINT, organizations=organizations,
                        settings=settings) as s:
        assert "Authorization" in s.headers
        assert s.headers["Authorization"] == 'Bearer blah'
