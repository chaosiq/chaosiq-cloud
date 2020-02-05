# -*- coding: utf-8 -*-
import pytest

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


def test_run_verification():
    journal = run_verification(ExperimentWithCompleteVerification)
    assert journal.get("deviated") is False
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
