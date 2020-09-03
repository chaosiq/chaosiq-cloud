# -*- coding: utf-8 -*-
from typing import Any, Dict

from chaoslib.caching import with_cache
from chaoslib.experiment import ensure_experiment_is_valid, \
    initialize_run_journal
from chaoslib.run import Runner, RunEventHandler
from chaoslib.types import (Experiment, Journal, Schedule,
                            Settings, Strategy)
from logzero import logger

from ..api.verification import VerificationRunEventHandler
from .exceptions import InvalidVerification

__all__ = ["ensure_verification_is_valid", "run_verification"]


@with_cache
def ensure_verification_is_valid(experiment: Experiment):
    ensure_experiment_is_valid(experiment)

    extensions = experiment.get("extensions")
    if extensions is None:
        raise InvalidVerification(
                "a verification must have an extensions block")

    chaosiq_blocks = list(filter(
        lambda extension: extension.get("name", "") == "chaosiq",
        extensions))

    if not len(chaosiq_blocks) == 1:
        raise InvalidVerification(
                "a verification must have a single chaosiq extension block")

    verification = chaosiq_blocks[0].get("verification")
    if verification is None:
        raise InvalidVerification(
                "a verification must have a verification block")

    id = verification.get("id")
    if id is None:
        raise InvalidVerification(
                "a verification must have an id")

    frequency_of_measurement = verification.get("frequency-of-measurement")
    if frequency_of_measurement is None:
        raise InvalidVerification(
                "a verification must have a frequency-of-measurement block")

    duration_of_conditions = verification.get("duration-of-conditions")
    if duration_of_conditions is None:
        raise InvalidVerification(
                "a verification must have a duration-of-conditions block")

    logger.info("Verification looks valid")


# pylama:ignore=C901
@with_cache
def run_verification(experiment: Experiment,
                     settings: Settings = None,
                     experiment_vars: Dict[str, Any] = None,
                     strategy: Strategy = Strategy.CONTINOUS,
                     schedule: Schedule = None) -> Journal:
    with Runner(strategy, schedule) as runner:
        runner.register_event_handler(RunEventHandler())
        runner.register_event_handler(
            VerificationRunEventHandler(experiment, settings))

        journal = initialize_run_journal(experiment)
        # TODO: remove with https://github.com/chaosiq/chaosiq-cloud/issues/70
        journal["measurements"] = []

        return runner.run(
            experiment, settings, journal=journal,
            experiment_vars=experiment_vars)
