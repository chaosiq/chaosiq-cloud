import requests
import requests_mock

from chaoscloud.api import urls
from chaoscloud.api.organization import request_orgs

ENDPOINT = "https://console.chaosiq.io"


def test_organization_are_fetched_for_user(organizations):
    with requests_mock.mock() as m:
        url = urls.org(urls.base(ENDPOINT))
        m.get(url, status_code=200, json=organizations)
        r = request_orgs(url, token="XYZ", verify_tls=True)
        assert r.status_code == 200
        assert r.json() == organizations


def test_organization_cannot_be_fetched_when_token_is_rejected():
    with requests_mock.mock() as m:
        url = urls.org(urls.base(ENDPOINT))
        m.get(url, status_code=401)
        r = request_orgs(url, token="XYZ", verify_tls=True)
        assert r.status_code == 401


def test_organization_cannot_be_fetched_ssl_error_is_raised():
    with requests_mock.mock() as m:
        url = urls.org(urls.base(ENDPOINT))
        m.get(url, exc=requests.exceptions.SSLError)
        r = request_orgs(url, token="XYZ", verify_tls=True)
        assert r is None
