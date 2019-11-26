import uuid

import requests
import requests_mock
import simplejson as json

from chaoscloud.api import client_session
from chaoscloud.api import urls
from chaoscloud.api.execution import initialize_execution, publish_execution, \
    fetch_execution, publish_event


ENDPOINT = "https://console.chaosiq.io"


def test_execution_not_created_when_experiment_is_invalid_type(
                                                organizations, default_org_id):
    experiment_id = str(uuid.uuid4())
    # the remote endpoint cannot deal with anything but a experiment
    experiment = {
        "extensions": [
            {
                "name": "chaosiq",
                "experiment_id": experiment_id
            }
        ]
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id,
            with_executions=True)
        m.post(
            url, status_code=422, json=[
                {
                    "loc": ["a_dict"],
                    "msg": "value is not a valid dict",
                    "type": "type_error.dict"
                }
            ],
            headers={
                "content-type": "application/json"
            }
        )
        with client_session(ENDPOINT, organizations) as s:
            r = initialize_execution(s, experiment, {})
            assert r.status_code == 422


def test_create_execution(organizations, default_org_id):
    experiment_id = str(uuid.uuid4())
    x_id = str(uuid.uuid4())
    experiment = {
        "title": "Hello there",
        "extensions": [
            {
                "name": "chaosiq",
                "experiment_id": experiment_id
            }
        ]
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id,
            with_executions=True)
        m.post(
            url, status_code=201,
            json={
                "id": x_id,
            },
            headers={
                "content-type": "application/json",
                "content-location": "{}/{}".format(url, x_id)
            }
        )
        with client_session(ENDPOINT, organizations) as s:
            r = initialize_execution(s, experiment, {})
            assert r.status_code == 201
            # we injected the execution_id
            assert experiment["extensions"][0]["execution_id"] == x_id


def test_cannot_create_execution_on_requests_connection_timeout(
                                                organizations, default_org_id):
    experiment_id = str(uuid.uuid4())
    experiment = {
        "title": "Hello there",
        "extensions": [
            {
                "name": "chaosiq",
                "experiment_id": experiment_id
            }
        ]
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id,
            with_executions=True)
        m.post(
            url,
            exc=requests.exceptions.ConnectTimeout
        )
        with client_session(ENDPOINT, organizations) as s:
            r = initialize_execution(s, experiment, {})
            assert r is None


def test_cannot_create_execution_from_unknown_experiment_id(
                                                organizations, default_org_id):
    experiment_id = str(uuid.uuid4())
    experiment = {
        "title": "Hello there",
        "extensions": [
            {
                "name": "chaosiq",
                "experiment_id": experiment_id
            }
        ]
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id,
            with_executions=True)
        m.post(
            url, status_code=422,
            json=[],
            headers={
                "content-type": "application/json"
            }
        )
        with client_session(ENDPOINT, organizations) as s:
            r = initialize_execution(s, experiment, {})
            assert r.status_code == 422
            assert "execution_id" not in experiment["extensions"][0]


def test_cannot_update_execution_with_invalid_execution_id(organizations,
                                                           default_org_id):
    experiment_id = str(uuid.uuid4())
    x_id = str(uuid.uuid4())
    journal = {
        "experiment": {
            "extensions": [
                {
                    "name": "chaosiq",
                    "execution_id": x_id,
                    "experiment_id": experiment_id
                }
            ]
        }
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id,
            execution_id=x_id)
        m.put(
            url, status_code=404,
            headers={
                "content-type": "text/plain"
            }
        )
        with client_session(ENDPOINT, organizations) as s:
            r = publish_execution(s, journal)
            assert r.status_code == 404


def test_update_execution(organizations, default_org_id):
    experiment_id = str(uuid.uuid4())
    x_id = str(uuid.uuid4())
    journal = {
        "experiment": {
            "extensions": [
                {
                    "name": "chaosiq",
                    "execution_id": x_id,
                    "experiment_id": experiment_id
                }
            ]
        }
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id, x_id)
        m.put(url, status_code=204)
        with client_session(ENDPOINT, organizations) as s:
            r = publish_execution(s, journal)
            assert r.status_code == 204


def test_cannot_update_execution_on_request_connection_timeout(organizations,
                                                               default_org_id):
    experiment_id = str(uuid.uuid4())
    x_id = str(uuid.uuid4())
    journal = {
        "experiment": {
            "extensions": [
                {
                    "name": "chaosiq",
                    "execution_id": x_id,
                    "experiment_id": experiment_id
                }
            ]
        }
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id, x_id)
        m.put(url, exc=requests.exceptions.ConnectTimeout)
        with client_session(ENDPOINT, organizations) as s:
            r = publish_execution(s, journal)
            assert r is None


def test_fetch_execution(organizations, default_org_id):
    experiment_id = str(uuid.uuid4())
    x_id = str(uuid.uuid4())
    journal = {
        "experiment": {
            "extensions": [
                {
                    "name": "chaosiq",
                    "execution_id": x_id,
                    "experiment_id": experiment_id
                }
            ]
        }
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id, x_id)
        m.get(url, json=journal)
        with client_session(ENDPOINT, organizations) as s:
            r = fetch_execution(s, journal)
            assert r.status_code == 200


def test_cannot_fetch_execution_on_request_connection_timeout(organizations,
                                                              default_org_id):
    experiment_id = str(uuid.uuid4())
    x_id = str(uuid.uuid4())
    journal = {
        "experiment": {
            "extensions": [
                {
                    "name": "chaosiq",
                    "execution_id": x_id,
                    "experiment_id": experiment_id
                }
            ]
        }
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id, x_id)
        m.get(url, exc=requests.exceptions.ConnectTimeout)
        with client_session(ENDPOINT, organizations) as s:
            r = fetch_execution(s, journal)
            assert r is None


def test_cannot_fetch_execution_non_published_experiment(organizations,
                                                         default_org_id):
    experiment_id = str(uuid.uuid4())
    x_id = str(uuid.uuid4())
    journal = {
        "experiment": {}
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id, x_id)
        m.get(url, exc=requests.exceptions.ConnectTimeout)
        with client_session(ENDPOINT, organizations) as s:
            r = fetch_execution(s, journal)
            assert r is None
            assert m.call_count == 0


def test_publish_event(organizations, default_org_id):
    experiment_id = str(uuid.uuid4())
    x_id = str(uuid.uuid4())
    extensions = [
        {
            "name": "chaosiq",
            "execution_id": x_id,
            "experiment_id": experiment_id
        }
    ]
    activity = {}
    run = {}
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id, x_id,
            with_events=True)
        m.post(url, status_code=201)
        with client_session(ENDPOINT, organizations) as s:
            publish_event(
                s, "start-experiment", activity, None, None, extensions, None,
                run)
            r = json.loads(m.last_request.body)
            assert r["specversion"] == "0.2"
            assert r["contenttype"] == "application/json"
            assert r["type"] == "start-experiment"
            assert r["source"] == "chaosiq-cloud"
            assert "id" in r
            assert "time" in r
            assert "data" in r
            assert "extensions" in r


def test_cannot_publish_event_non_published_execution(organizations,
                                                      default_org_id):
    experiment_id = str(uuid.uuid4())
    x_id = str(uuid.uuid4())
    extensions = []
    activity = {}
    run = {}
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id, x_id,
            with_events=True)
        m.post(url, status_code=201)
        with client_session(ENDPOINT, organizations) as s:
            publish_event(
                s, "start-experiment", activity, None, None, extensions, None,
                run)
            assert m.call_count == 0


def test_initialize_execution_requires_experiment_id():
    assert initialize_execution(None, {}, {}) is None
