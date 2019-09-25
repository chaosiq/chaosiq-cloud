import uuid

from chaoslib.exceptions import InterruptExecution
import pytest
import requests_mock

from chaoscloud.api import client_session
from chaoscloud.api.safeguard import is_allowed_to_continue
from chaoscloud.api import urls

ENDPOINT = "https://console.chaosiq.io"


def test_no_check_when_execution_is_not_found(organizations, default_org_id):
    execution_id = str(uuid.uuid4())
    experiment_id = str(uuid.uuid4())
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id,
            execution_id=execution_id, with_safeguards=True)
        m.get(url, status_code=404)
        try:
            with client_session(ENDPOINT, organizations) as s:
                is_allowed_to_continue(s, [
                    {
                        "name": "chaosiq",
                        "execution_id": execution_id,
                        "experiment_id": experiment_id
                    }
                ])
        except InterruptExecution:
            pytest.fail(
                "Missing execution identifier in experiment should not "
                "lead to execution interruption")


def test_interrupt_experiment(organizations, default_org_id):
    execution_id = str(uuid.uuid4())
    experiment_id = str(uuid.uuid4())
    with requests_mock.mock() as m:
        url = urls.full(
            urls.base(ENDPOINT), default_org_id, experiment_id,
            execution_id=execution_id, with_safeguards=True)
        m.get(
            url,
            status_code=200,
            json={
                "allowed": False,
                "policies": [
                    {
                        "name": "godzilla says stop"
                    }
                ]
            })
        with client_session(ENDPOINT, organizations) as s:
            with pytest.raises(InterruptExecution):
                is_allowed_to_continue(s, [
                    {
                        "name": "chaosiq",
                        "execution_id": execution_id,
                        "experiment_id": experiment_id
                    }
                ])
