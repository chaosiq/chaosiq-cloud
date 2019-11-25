import uuid

import requests_mock

from chaoscloud.api import urls
from chaoscloud.controls import configure_control, after_experiment_control

ENDPOINT = "https://chaosiq.io"


def test_configure_control_creates_experiment_and_execution_when_new(
                                                organizations, default_org_id,
                                                settings):
    x_id = str(uuid.uuid4())
    e_id = str(uuid.uuid4())
    extensions = [
        {
            "name": "chaosiq"
        }
    ]
    experiment = {
        "title": "Hello there",
        "extensions": extensions
    }

    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, with_experiments=True)
        m.post(
            url, status_code=201,
            json={
                "id": e_id
            },
            headers={
                "content-type": "application/json",
                "content-location": "{}/{}".format(url, e_id)
            }
        )

        url = urls.full(
            urls.base(ENDPOINT), default_org_id, e_id, with_executions=True)
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

        configure_control(
            experiment, settings, url=ENDPOINT, organizations=organizations)
        assert experiment["extensions"][0]["experiment_id"] == e_id
        assert experiment["extensions"][0]["execution_id"] == x_id


def test_experiment_id_must_be_stored_in_journal(
        organizations, default_org_id, settings):
    x_id = str(uuid.uuid4())
    e_id = str(uuid.uuid4())
    ev_id = str(uuid.uuid4())
    extensions = [
        {
            "name": "chaosiq",
            "experiment_id": e_id,
            "execution_id": x_id
        }
    ]
    experiment = {
        "title": "Hello there",
        "extensions": extensions
    }
    journal = {
        "experiment": experiment
    }

    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, with_experiments=True)
        m.post(
            url, status_code=201,
            json={
                "id": e_id
            },
            headers={
                "content-type": "application/json",
                "content-location": "{}/{}".format(url, e_id)
            }
        )

        url = urls.full(
            urls.base(ENDPOINT), default_org_id, e_id, with_executions=True)
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

        url = urls.full(
            urls.base(ENDPOINT), default_org_id, e_id, x_id,
            with_executions=True, with_events=True)
        m.post(
            url, status_code=201,
            json={
                "id": ev_id,
            },
            headers={
                "content-type": "application/json",
                "content-location": "{}/{}".format(url, ev_id)
            }
        )

        url = urls.full(
            urls.base(ENDPOINT), default_org_id, e_id, x_id,
            with_executions=True, with_safeguards=True)
        m.get(
            url, status_code=201,
            json={
                "allowed": True
            },
            headers={
                "content-type": "application/json"
            }
        )

        url = urls.full(
            urls.base(ENDPOINT), default_org_id, e_id, x_id,
            with_executions=True)
        m.put(
            url, status_code=204,
            json={
            },
            headers={
                "content-type": "application/json"
            }
        )

        after_experiment_control(
            experiment, journal, extensions=extensions,
            url=ENDPOINT, organizations=organizations,
            settings=settings)
        assert journal["extensions"][0]["experiment_id"] == e_id
        assert journal["extensions"][0]["execution_id"] == x_id
