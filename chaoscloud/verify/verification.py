# -*- coding: utf-8 -*-
import threading
import time

from chaoslib.caching import with_cache
import chaoslib.experiment
from chaoslib.types import Experiment, Settings
from logzero import logger

from chaoscloud.verify.exceptions import InvalidVerification

__all__ = ["ensure_verification_is_valid", "run_verification"]


@with_cache
def ensure_verification_is_valid(experiment: Experiment):
    chaoslib.experiment.ensure_experiment_is_valid(experiment)

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

    measurements_experiment = build_measurements_experiment(experiment)
    extensions = measurements_experiment.get("extensions")
    chaosiq_blocks = list(filter(
        lambda extension: extension.get("name", "") == "chaosiq",
        extensions))
    verification = chaosiq_blocks[0].get("verification")
    frequency = verification.get("frequency-of-measurement")

    stop_measurements_event = threading.Event()
    measurements_thread = threading.Thread(target=run_measurements_experiment,
                                           args=(stop_measurements_event,
                                                 measurements_experiment,
                                                 settings, frequency))
    measurements_thread.start()

    duration_of_conditions = verification.get("duration-of-conditions")
    time.sleep(duration_of_conditions)
    stop_measurements_event.set()
    measurements_thread.join()

    logger.info(
        "Finished running verification: {t}".format(t=experiment["title"]))


###############################################################################
# Internals
###############################################################################
def build_measurements_experiment(experiment: Experiment):
    if has_steady_state_hypothesis_with_probes(experiment):
        experiment["method"] = []
        experiment["rollbacks"] = []
        return experiment
    return None


def has_steady_state_hypothesis_with_probes(experiment: Experiment):
    steady_state_hypothesis = experiment.get("steady-state-hypothesis")
    if steady_state_hypothesis:
        probes = steady_state_hypothesis.get("probes")
        if probes:
            return len(probes) > 0
    return None


def run_measurements_experiment(stop_measurements_event: threading.Event,
                                experiment: Experiment, settings: Settings,
                                frequency: int):
    measurements_count = 0
    logger.info(
        "Starting measurements for verification: {t}, frequency: {f} seconds"
        .format(t=experiment["title"], f=frequency))
    while not stop_measurements_event.is_set():
        measurements_count += 1
        logger.info(
            "Running measurements for verification: {t}, measurement: {i}"
            .format(t=experiment["title"], i=measurements_count))
        run_experiment(experiment, settings)
        time.sleep(frequency)

    logger.info(
        "Stopping measurements for verification: {t}. {c} measurements taken"
        .format(t=experiment["title"], c=measurements_count))


def run_experiment(experiment: Experiment, settings: Settings):
    chaoslib.experiment.run_experiment(experiment, settings)
