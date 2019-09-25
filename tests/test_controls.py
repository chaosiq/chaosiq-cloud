import uuid

import requests_mock

from chaoscloud.api import urls
from chaoscloud.controls import configure_control

ENDPOINT = "https://chaosiq.io"


def test_configure_control_creates_experiment_and_execution_when_new(
                                                organizations, default_org_id):
    x_id = str(uuid.uuid4())
    e_id = str(uuid.uuid4())
    experiment = {
        "title": "Hello there",
        "extensions": [
            {
                "name": "chaosiq"
            }
        ]
    }
    settings = {}

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
