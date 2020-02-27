# -*- coding: utf-8 -*-
from copy import deepcopy
import platform
import threading
import time
from datetime import datetime

from chaoslib import __version__
from chaoslib.caching import with_cache
from chaoslib.configuration import load_configuration
from chaoslib.control import (Control, cleanup_controls,
                              cleanup_global_controls, initialize_controls,
                              initialize_global_controls)
from chaoslib.exceptions import ChaosException, InterruptExecution
from chaoslib.experiment import (apply_activities, apply_rollbacks,
                                 ensure_experiment_is_valid,
                                 get_background_pools,
                                 run_steady_state_hypothesis)
from chaoslib.secret import load_secrets
from chaoslib.settings import get_loaded_settings
from chaoslib.types import (Configuration, Experiment, Journal, Secrets,
                            Settings)
from logzero import logger

from ..api.verification import verification_run, VerificationRunEventHandler
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
                     settings: Settings = None) -> Journal:
    with verification_run(experiment, settings) as run:
        journal = initialize_verification_run_journal(experiment)
        try:
            run_id = run.start(journal)
        except InterruptExecution as i:
            logger.fatal(str(i))
            return

        if run_id:
            logger.info("Started run '{r}' of verification '{t}'".format(
                r=run_id, t=experiment["title"]))
        else:
            logger.warning(
                "As we failed to declare this run to ChaosIQ, the "
                "verification will carry on but will not be reported.")

        dry = experiment.get("dry", False)
        if dry:
            logger.warning("Dry mode enabled")

        started_at = time.time()
        settings = settings if settings is not None else get_loaded_settings()
        config = load_configuration(experiment.get("configuration", {}))
        secrets = load_secrets(experiment.get("secrets", {}), config)
        initialize_global_controls(experiment, config, secrets, settings)
        initialize_controls(experiment, config, secrets)
        activity_pool, rollback_pool = get_background_pools(experiment)

        control = Control()
        stop_measurements_event = threading.Event()
        try:
            try:
                control.begin(
                    "experiment", experiment, experiment, config, secrets)

                extensions = experiment.get("extensions")
                chaosiq_blocks = list(filter(
                    lambda extension: extension.get("name", "") == "chaosiq",
                    extensions))
                verification = chaosiq_blocks[0].get("verification")
                frequency = verification.get("frequency-of-measurement")

                measurements_thread = threading.Thread(
                    target=run_measurements_experiment,
                    args=(
                        stop_measurements_event, experiment, frequency,
                        settings, config, secrets, journal, run, dry)
                    )
                measurements_thread.start()

                warm_up_duration = verification.get("warm-up-duration")
                logger.info(
                    "Starting verification warm-up period of {} "
                    "seconds".format(warm_up_duration))
                pause_for_duration(warm_up_duration)
                logger.info("Finished verification warm-up")

                logger.info("Triggering verification conditions")
                try:
                    run.start_condition()
                    state = apply_activities(
                        experiment, config, secrets, activity_pool, dry)
                    journal["run"] = state
                    run.condition_completed(state)
                except InterruptExecution:
                    raise
                except Exception:
                    journal["status"] = "aborted"
                    logger.fatal(
                        "Verification ran into an unexpected fatal error, "
                        "aborting now.", exc_info=True)
                logger.info("Finished triggering verification conditions")

                duration_of_conditions = verification.get(
                    "duration-of-conditions")
                logger.info("Starting verification conditions for {} seconds"
                            .format(duration_of_conditions))
                pause_for_duration(duration_of_conditions)
                logger.info("Finished verification conditions duration")

                cool_down_duration = verification.get("cool-down-duration")
                logger.info(
                    "Starting verification cool-down period of "
                    "{} seconds".format(cool_down_duration))
                run.start_cooldown(cool_down_duration)
                pause_for_duration(cool_down_duration)
                run.cooldown_completed()
                logger.info("Finished verification cool-down period"
                            .format(t=experiment["title"]))
            except InterruptExecution as i:
                run.interrupt()
                journal["status"] = "interrupted"
                logger.fatal(str(i))
                stop_measurements_event.set()
                measurements_thread.join()
            except (KeyboardInterrupt, SystemExit):
                run.signal_exit()
                journal["status"] = "interrupted"
                logger.warning(
                    "Received an exit signal, "
                    "leaving without applying rollbacks.")
                stop_measurements_event.set()
                measurements_thread.join()
            else:
                if journal["status"] == "running":
                    journal["status"] = "completed"
                stop_measurements_event.set()
                measurements_thread.join()
                logger.info("Triggering any verification rollbacks")
                try:
                    journal["rollbacks"] = apply_rollbacks(
                        experiment, config, secrets, rollback_pool, dry)
                except InterruptExecution as i:
                    journal["status"] = "interrupted"
                    logger.fatal(str(i))
                except (KeyboardInterrupt, SystemExit):
                    journal["status"] = "interrupted"
                    logger.warning(
                        "Received an exit signal."
                        "Terminating now without running the remaining "
                        "rollbacks.")
                logger.info(
                    "Finished triggering any verification rollbacks")
            journal["end"] = datetime.utcnow().isoformat()
            journal["duration"] = time.time() - started_at

            control.with_state(journal)

            try:
                control.end(
                    "experiment", experiment, experiment, config, secrets)
            except ChaosException:
                logger.debug("Failed to close controls", exc_info=True)

            logger.info(
                "Finished running verification: {}".format(
                    experiment["title"]))
        finally:
            cleanup_controls(experiment)
            cleanup_global_controls()

        run.finish(journal)
    return journal


###############################################################################
# Internals
###############################################################################
def has_steady_state_hypothesis_with_probes(experiment: Experiment):
    steady_state_hypothesis = experiment.get("steady-state-hypothesis")
    if steady_state_hypothesis:
        probes = steady_state_hypothesis.get("probes")
        if probes:
            return len(probes) > 0
    return None


def run_measurements_experiment(stop_measurements_event: threading.Event,
                                experiment: Experiment,
                                frequency: int, settings: Settings,
                                config: Configuration, secrets: Secrets,
                                journal: Journal,
                                run_event_handler: VerificationRunEventHandler,
                                dry: bool = False):
    run_event_handler.start_measurements(frequency)
    measurements_count = 0
    logger.info("Starting verification measurement every {} seconds"
                .format(frequency))
    while not stop_measurements_event.is_set():
        measurements_count += 1
        logger.info(
            "Running verification measurement {}"
            .format(measurements_count))
        state = run_steady_state_hypothesis(
            deepcopy(experiment), config, secrets, dry=dry)
        run_event_handler.measurement_sample(measurements_count, state)
        journal["measurements"].append(state)
        time.sleep(frequency)

    run_event_handler.measurements_completed()
    logger.info("Stopping verification measurements. {} measurements taken"
                .format(measurements_count))


def pause_for_duration(duration):
    if duration:
        time.sleep(duration)


def initialize_verification_run_journal(experiment: Experiment) -> Journal:
    return {
        "chaoslib-version": __version__,
        "platform": platform.platform(),
        "node": platform.node(),
        "experiment": experiment.copy(),
        "start": datetime.utcnow().isoformat(),
        "status": None,
        "deviated": False,
        "measurements": [],
        "run": [],
        "rollbacks": []
    }
