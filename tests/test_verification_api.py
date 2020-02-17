# -*- coding: utf-8 -*-
from typing import Any, Dict
from unittest.mock import patch
import uuid

import requests_mock

from chaoscloud.api import urls
from chaoscloud.api.verification import verification_run, \
    VerificationRunEventHandler

ENDPOINT = "https://chaosiq.io"


@patch("chaoscloud.api.build_base_url", autospec=True)
def test_start_run(build_base_url, base_team_url: str, default_org_id: str,
                   default_team_id: str, default_settings: Dict[str, Any]):
    experiment_id = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    verification_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())

    experiment = {
        "title": "hello",
        "extensions": [
            {
                "name": "chaosiq",
                "verification": {
                    "id": verification_id
                },
                "experiment_id": experiment_id,
                "execution_id": execution_id
            }
        ]
    }

    journal = {
        "title":  "hello there"
    }

    build_base_url.return_value = base_team_url
    with requests_mock.mock() as m:
        url = urls.execution(
            urls.experiment(base_team_url, experiment_id=experiment_id))
        x_url = urls.execution(
            urls.experiment(base_team_url, experiment_id=experiment_id),
            execution_id=execution_id)
        m.post(url, status_code=201, json={
            "id": experiment_id
        }, headers={
            "content-location": x_url
        })

        url = urls.verification_run(
            urls.verification(
                base_team_url, verification_id=verification_id))
        m.post(url, status_code=201, json={
            "id": run_id,
            "org_id": default_org_id,
            "team_id": default_team_id,
            "verification_id": verification_id,
            "experiment_id": experiment_id,
            "execution_id": execution_id,
            "state": "running",
            "status": "",
            "journal": journal
        })
        run = VerificationRunEventHandler(experiment, default_settings)
        run_id = run.start(journal)
        assert m.called
        assert run_id == run_id


@patch("chaoscloud.api.build_base_url", autospec=True)
def test_failing_run_start_returns_nothing(build_base_url, base_team_url: str,
                                           default_org_id: str,
                                           default_team_id: str,
                                           default_settings: Dict[str, Any]):
    experiment_id = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    verification_id = str(uuid.uuid4())

    experiment = {
        "title": "hello",
        "extensions": [
            {
                "name": "chaosiq",
                "verification": {
                    "id": verification_id
                },
                "experiment_id": experiment_id,
                "execution_id": execution_id
            }
        ]
    }

    build_base_url.return_value = base_team_url
    with requests_mock.mock() as m:
        url = urls.execution(
            urls.experiment(base_team_url, experiment_id=experiment_id))
        x_url = urls.execution(
            urls.experiment(base_team_url, experiment_id=experiment_id),
            execution_id=execution_id)
        m.post(url, status_code=201, json={
            "id": experiment_id
        }, headers={
            "content-location": x_url
        })
        m.base_url = base_team_url
        url = urls.verification_run(
            urls.verification(
                base_team_url, verification_id=verification_id))
        m.post(url, exc=RuntimeError)
        run = VerificationRunEventHandler(experiment, default_settings)
        r = run.start({})
        assert r is None
        assert m.called


@patch("chaoscloud.api.build_base_url", autospec=True)
def test_handle_start_event(build_base_url, base_team_url: str,
                            default_org_id: str, default_team_id: str,
                            default_settings: Dict[str, Any]):
    experiment_id = str(uuid.uuid4())
    execution_id = str(uuid.uuid4())
    verification_id = str(uuid.uuid4())
    run_id = str(uuid.uuid4())

    experiment = {
        "title": "hello",
        "extensions": [
            {
                "name": "chaosiq",
                "verification": {
                    "id": verification_id
                },
                "experiment_id": experiment_id,
                "execution_id": execution_id
            }
        ]
    }

    journal = {
        "title":  "hello there"
    }

    build_base_url.return_value = base_team_url
    with requests_mock.mock() as m:
        url = urls.execution(
            urls.experiment(base_team_url, experiment_id=experiment_id))
        x_url = urls.execution(
            urls.experiment(base_team_url, experiment_id=experiment_id),
            execution_id=execution_id)
        m.post(url, status_code=201, json={
            "id": experiment_id
        }, headers={
            "content-location": x_url
        })
        url = urls.verification_run(
            urls.verification(
                base_team_url, verification_id=verification_id))
        m.post(url, status_code=201, json={
            "id": run_id,
            "org_id": default_org_id,
            "team_id": default_team_id,
            "verification_id": verification_id,
            "experiment_id": experiment_id,
            "execution_id": execution_id,
            "state": "running",
            "status": "",
            "journal": journal
        })

        with verification_run(experiment, default_settings) as run:
            r = run.start(journal)
            assert m.called
            assert r == run_id
