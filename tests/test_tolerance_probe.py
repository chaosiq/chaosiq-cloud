from chaoscloud.probes.http import read_http_status_code, time_http_call

from chaoslib.exceptions import ActivityFailed
import pytest
import requests
import requests_mock


def test_read_http_status_code_ok():
    with requests_mock.Mocker() as m:
        m.get("http://example.com/hello")
        assert read_http_status_code("http://example.com/hello") == 200


def test_read_http_status_code_ko_on_connection_timeout():
    with requests_mock.Mocker() as m:
        m.get(
            "http://example.com/hello",
            exc=requests.exceptions.ConnectTimeout)

        with pytest.raises(ActivityFailed):
            read_http_status_code("http://example.com/hello")


def test_time_http_call_ok():
    with requests_mock.Mocker() as m:
        m.get("http://example.com/hello")
        assert time_http_call("http://example.com/hello") < 100.0


def test_time_http_call_ko_on_connection_timeout():
    with requests_mock.Mocker() as m:
        m.get(
            "http://example.com/hello",
            exc=requests.exceptions.ConnectTimeout)

        with pytest.raises(ActivityFailed):
            time_http_call("http://example.com/hello")
