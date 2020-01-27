# -*- coding: utf-8 -*-
import threading
import time

import chaoslib.experiment
from chaoslib.caching import with_cache
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

    extensions = experiment.get("extensions")
    chaosiq_blocks = list(filter(
        lambda extension: extension.get("name", "") == "chaosiq",
        extensions))
    verification = chaosiq_blocks[0].get("verification")
    frequency = verification.get("frequency-of-measurement")

    measurements_experiment = build_measurements_experiment(experiment)

    stop_measurements_event = threading.Event()
    measurements_thread = threading.Thread(target=run_measurements_experiment,
                                           args=(stop_measurements_event,
                                                 measurements_experiment,
                                                 settings, frequency))
    measurements_thread.start()

    warm_up_duration = verification.get("warm-up-duration")
    logger.info(
        "Starting warm-up period for verification: {t}, duration: {d} seconds"
        .format(t=experiment["title"], d=warm_up_duration))
    pause_for_duration(warm_up_duration)
    logger.info(
        "Finished warm-up period for verification: {t}"
        .format(t=experiment["title"]))

    conditions_experiment = build_conditions_experiment(experiment)
    logger.info(
        "Triggering conditions for verification: {t}".format(
            t=conditions_experiment["title"]))
    run_experiment(conditions_experiment, settings)
    logger.info(
        "Finished triggering conditions for verification: {t}".format(
            t=conditions_experiment["title"]))

    duration_of_conditions = verification.get("duration-of-conditions")
    logger.info(
        ("Starting duration for conditions for verification: {t}, "
         "duration: {d} seconds").format(
            t=experiment["title"],
            d=duration_of_conditions))
    pause_for_duration(duration_of_conditions)
    logger.info(
        "Finished duration for conditions for verification: {t}"
        .format(t=experiment["title"]))

    cool_down_duration = verification.get("cool-down-duration")
    logger.info(
        ("Starting cool-down period for verification: {t}, "
         "duration: {d} seconds").format(
             t=experiment["title"],
             d=cool_down_duration))
    pause_for_duration(cool_down_duration)
    logger.info(
        "Finished cool-down period for verification: {t}"
        .format(t=experiment["title"]))

    stop_measurements_event.set()
    measurements_thread.join()

    rollbacks_experiment = build_rollbacks_experiment(experiment)
    logger.info(
        "Triggering any rollbacks for verification: {t}".format(
            t=rollbacks_experiment["title"]))
    run_experiment(rollbacks_experiment, settings)
    logger.info(
        "Finished triggering any rollbacks for verification: {t}".format(
            t=conditions_experiment["title"]))

    logger.info(
        "Finished running verification: {t}".format(t=experiment["title"]))


###############################################################################
# Internals
###############################################################################
def build_measurements_experiment(experiment: Experiment):
    measurements_experiment = experiment.copy()
    if has_steady_state_hypothesis_with_probes(measurements_experiment):
        measurements_experiment["method"] = []
        measurements_experiment["rollbacks"] = []
        return measurements_experiment
    return None


def build_conditions_experiment(experiment: Experiment):
    conditions_experiment = experiment.copy()
    conditions_experiment["steady-state-hypothesis"] = {}
    conditions_experiment["rollbacks"] = []
    return conditions_experiment


def build_rollbacks_experiment(experiment: Experiment):
    rollbacks_experiment = experiment.copy()
    rollbacks_experiment["steady-state-hypothesis"] = {}
    rollbacks_experiment["method"] = []
    return rollbacks_experiment


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


def pause_for_duration(duration):
    if duration:
        time.sleep(duration)
