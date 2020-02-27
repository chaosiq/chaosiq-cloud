# -*- coding: utf-8 -*-
from copy import deepcopy
from typing import Any, Dict
from unittest.mock import patch
import uuid

import pytest
import requests_mock

from chaoscloud.api import urls
from chaoscloud.verify.exceptions import InvalidVerification
from chaoscloud.verify.verification import (
    ensure_verification_is_valid, has_steady_state_hypothesis_with_probes,
    run_verification)
from fixtures.verifications import (
    ExperimentWithCompleteVerification,
    ExperimentWithNoSteadyStateHypothesisProbes,
    ExperimentWithoutChaosIQExtensionBlock,
    ExperimentWithoutChaosIQVerificationBlock,
    ExperimentWithoutConditionsDuration, ExperimentWithoutExtensionBlock,
    ExperimentWithoutMeasurementFrequency, ExperimentWithoutVerificationId,
    ExperimentWithSteadyStateHypothesWithProbe)

ENDPOINT = "https://chaosiq.io"


@patch("chaoscloud.api.build_base_url", autospec=True)
def test_run_verification(build_base_url: str, base_team_url: str,
                          default_org_id: str, default_team_id: str,
                          default_settings: Dict[str, Any]):
    verification_id = "9d9b8854-9bc0-4b64-873c-65ddabb0e5f8"
    experiment_id = "25fe4625-ab86-4db1-8f0c-e48ed7db402e"
    execution_id = "0e0c725b-597a-4740-a55f-23d71966ab5d"
    run_id = str(uuid.uuid4())
    journal = {}

    experiment = deepcopy(ExperimentWithCompleteVerification)
    experiment["extensions"][0]["verification"]["id"] = verification_id

    build_base_url.return_value = base_team_url
    with requests_mock.mock() as m:
        m.get("http://blah.com")

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
        finished_url = "{}/{}/finished".format(url, run_id)
        m.post(finished_url, status_code=204, json={})

        url = urls.verification_run_events(
            urls.verification_run(
                urls.verification(
                    base_team_url, verification_id=verification_id),
                verification_run_id=run_id))
        m.post(url, status_code=201, json={})
        journal = run_verification(experiment, default_settings)
        assert journal.get("deviated") is False
        assert journal["status"] == "completed"
        assert len(journal.get("measurements")) > 1


def test_verification_without_extension_block_is_invalid():
    with pytest.raises(InvalidVerification) as exc:
        ensure_verification_is_valid(
            ExperimentWithoutExtensionBlock)
    assert "a verification must have an extensions block" in str(exc.value)


def test_verification_without_chaosiq_extension_is_invalid():
    with pytest.raises(InvalidVerification) as exc:
        ensure_verification_is_valid(
            ExperimentWithoutChaosIQExtensionBlock)
    assert "a verification must have a single chaosiq extension block" in \
        str(exc.value)


def test_verification_without_verification_block_is_invalid():
    with pytest.raises(InvalidVerification) as exc:
        ensure_verification_is_valid(
            ExperimentWithoutChaosIQVerificationBlock)
    assert "a verification must have a verification block" in \
        str(exc.value)


def test_verification_without_id_is_invalid():
    with pytest.raises(InvalidVerification) as exc:
        ensure_verification_is_valid(
            ExperimentWithoutVerificationId)
    assert "a verification must have an id" in \
        str(exc.value)


def test_verification_without_frequency_is_invalid():
    with pytest.raises(InvalidVerification) as exc:
        ensure_verification_is_valid(
            ExperimentWithoutMeasurementFrequency)
    assert "a verification must have a frequency-of-measurement block" in \
        str(exc.value)


def test_verification_without_conditions_duration_is_invalid():
    with pytest.raises(InvalidVerification) as exc:
        ensure_verification_is_valid(
            ExperimentWithoutConditionsDuration)
    assert "a verification must have a duration-of-conditions block" in \
        str(exc.value)


def test_has_steady_state_hypothesis_when_has_a_probe():
    assert has_steady_state_hypothesis_with_probes(
        ExperimentWithSteadyStateHypothesWithProbe) is not None


def test_has_no_steady_state_hypothesis_when_has_no_probes():
    assert has_steady_state_hypothesis_with_probes(
        ExperimentWithNoSteadyStateHypothesisProbes) is None
