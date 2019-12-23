import uuid

import requests
import requests_mock

from chaoscloud.api import client_session, urls
from chaoscloud.api.experiment import publish_experiment

ENDPOINT = "https://chaosiq.io"


def test_experiment_not_created_when_invalid_type(organizations,
                                                  default_org_id,
                                                  default_team_id):
    # the remote endpoint cannot deal with anything but a experiment
    experiment = []
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, default_team_id,
            with_experiments=True)
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
            r = publish_experiment(s, experiment)
            assert r.status_code == 422
            assert experiment == []


def test_experiment_not_created_when_unmodified(
        organizations, default_org_id, default_team_id):
    experiment = {
        "title": "hello"
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, default_team_id,
            with_experiments=True)
        m.post(
            url, status_code=204
        )
        with client_session(ENDPOINT, organizations) as s:
            r = publish_experiment(s, experiment)
            assert r.status_code == 204


def test_create_experiment(organizations, default_org_id, default_team_id):
    x_id = str(uuid.uuid4())
    experiment = {
        "title": "hello"
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, default_team_id,
            with_experiments=True)
        m.post(
            url, status_code=201,
            json={
                "id": x_id
            },
            headers={
                "content-type": "application/json",
                "content-location": "{}/{}".format(url, x_id)
            }
        )
        with client_session(ENDPOINT, organizations) as s:
            r = publish_experiment(s, experiment)
            assert r.status_code == 201
            assert r.headers["content-location"] == "{}/{}".format(url, x_id)


def test_cannot_create_experiment_on_requests_connection_timeout(
                                                organizations, default_org_id,
                                                default_team_id):
    experiment = {
        "title": "hello"
    }
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, default_team_id,
            with_experiments=True)
        m.post(
            url, exc=requests.exceptions.ConnectTimeout
        )
        with client_session(ENDPOINT, organizations) as s:
            r = publish_experiment(s, experiment)
            assert r is None
