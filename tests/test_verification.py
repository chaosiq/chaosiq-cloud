# -*- coding: utf-8 -*-
from unittest.mock import patch

import pytest

from chaoscloud.verify.exceptions import InvalidVerification
from chaoscloud.verify.verification import (
    build_conditions_experiment, build_measurements_experiment,
    build_rollbacks_experiment, ensure_verification_is_valid,
    has_steady_state_hypothesis_with_probes, run_verification)
from fixtures.verifications import (
    ExperimentWithCompleteVerification, ExperimentWithNoSteadyStateHypothesis,
    ExperimentWithNoSteadyStateHypothesisProbes,
    ExperimentWithoutChaosIQExtensionBlock,
    ExperimentWithoutChaosIQVerificationBlock,
    ExperimentWithoutConditionsDuration, ExperimentWithoutExtensionBlock,
    ExperimentWithoutMeasurementFrequency, ExperimentWithoutVerificationId,
    ExperimentWithSteadyStateHypothesWithProbe)


@patch('chaoscloud.verify.verification.run_experiment')
def test_run_verification(run_experiment):
    run_verification(ExperimentWithCompleteVerification)
    assert run_experiment.called
    assert run_experiment.call_count == 9


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


def test_measurements_experiment_built_when_steady_state_complete():
    measurements_experiment = build_measurements_experiment(
        ExperimentWithCompleteVerification)
    assert measurements_experiment is not None
    assert len(measurements_experiment.get("method")) == 0
    assert len(measurements_experiment.get("rollbacks")) == 0


def test_no_measurements_experiment_built_when_no_steady_state_hypothesis():
    assert build_measurements_experiment(
        ExperimentWithNoSteadyStateHypothesis) is None


def test_has_steady_state_hypothesis_when_has_a_probe():
    assert has_steady_state_hypothesis_with_probes(
        ExperimentWithSteadyStateHypothesWithProbe) is not None


def test_has_no_steady_state_hypothesis_when_has_no_probes():
    assert has_steady_state_hypothesis_with_probes(
        ExperimentWithNoSteadyStateHypothesisProbes) is None


def test_build_conditions_experiment():
    conditions_experiment = build_conditions_experiment(
        ExperimentWithCompleteVerification)
    assert len(conditions_experiment.get("steady-state-hypothesis")) == 0
    assert len(conditions_experiment.get("rollbacks")) == 0


def test_build_rollbacks_experiment():
    rollbacks_experiment = build_rollbacks_experiment(
        ExperimentWithCompleteVerification)
    assert len(rollbacks_experiment.get("steady-state-hypothesis")) == 0
    assert len(rollbacks_experiment.get("method")) == 0
