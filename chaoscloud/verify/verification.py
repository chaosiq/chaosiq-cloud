# -*- coding: utf-8 -*-
from chaoslib.caching import with_cache
from chaoslib.experiment import ensure_experiment_is_valid
from chaoslib.types import Experiment, Settings
from logzero import logger

from chaoscloud.verify.exceptions import InvalidVerification

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


@with_cache
def run_verification(experiment: Experiment,
                     settings: Settings = None):
    logger.info("Running verification: {t}".format(t=experiment["title"]))
