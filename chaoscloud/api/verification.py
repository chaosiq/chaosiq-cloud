# -*- coding: utf-8 -*-
from datetime import datetime
import time
from typing import Any, Dict, Optional, Tuple

from chaoslib.exceptions import InterruptExecution
from chaoslib.types import Experiment, Journal, Settings
from logzero import logger
import requests

from ..exceptions import MissingVerificationIdentifier
from ..extension import remove_sensitive_extension_values
from ..settings import get_endpoint_url, get_verify_tls, get_orgs
from ..types import Organizations
from .experiment import get_experiment_id
from .execution import initialize_execution
from . import client_session
from . import urls

__all__ = ["VerificationRunEventHandler", "get_run_id"]


###############################################################################
# Internals
###############################################################################
def get_verification_id(experiment: Experiment) -> str:
    extensions = experiment.get("extensions", [])
    for extension in extensions:
        if extension["name"] == "chaosiq":
            return extension.get("verification", {}).get("id")


def get_call_context(settings: Settings) -> Tuple[str, bool, Organizations]:
    base_endpoint = get_endpoint_url(settings)
    orgs = get_orgs(settings)
    verify_tls = get_verify_tls(settings)
    return base_endpoint, verify_tls, orgs


def set_run_id(verification_run_id: str, experiment: Experiment) -> None:
    extensions = experiment.setdefault("extensions", [])
    for extension in extensions:
        if extension["name"] == "chaosiq":
            extension["verification"]["run_id"] = verification_run_id
            break


def get_run_id(experiment: Experiment) -> str:
    extensions = experiment.get("extensions", [])
    for extension in extensions:
        if extension["name"] == "chaosiq":
            return extension.get("verification", {}).get("run_id")


class VerificationRunEventHandler:
    def __init__(self, experiment: Experiment, settings: Settings) -> None:
        """
        verification run handler for the Chaos Toolkit mainloop. Its purpose
        is to notify the ChaosIQ services of various steps in the process.
        """
        self.verification_id = get_verification_id(experiment)
        self.experiment = experiment
        self.settings = settings
        self.run_id = None
        self._start_time = None

        if not self.verification_id:
            logger.error(
                "Verification identifier not found in experiment under the "
                "ChaosIQ extensions. Without it, the process has to terminate."
            )
            raise MissingVerificationIdentifier()

    @property
    def initialized(self) -> bool:
        return self.run_id is not None

    @property
    def verification_run_path(self) -> str:
        return urls.verification_run(
            urls.verification(
                "", verification_id=self.verification_id
            )
        )

    @property
    def verification_run_event_path(self) -> str:
        return urls.verification_run_events(
            urls.verification_run(
                urls.verification(
                    "", verification_id=self.verification_id
                ),
                verification_run_id=self.run_id
            )
        )

    @property
    def verification(self) -> Dict[str, Any]:
        extensions = self.experiment.get("extensions")
        chaosiq_blocks = list(filter(
            lambda extension: extension.get("name", "") == "chaosiq",
            extensions))
        return chaosiq_blocks[0].get("verification")

    def get_error(self, r: requests.Response) -> Any:
        if (r is not None) and (r.status_code > 399):
            is_json = 'application/json' in r.headers.get(
                "content-type", '')
            error = (r.json() if is_json else r.text) or r.reason
            return error

    def _make_call(self, method: str, url: str,
                   **kwargs) -> Optional[requests.Response]:
        base_endpoint, verify_tls, orgs = get_call_context(self.settings)
        with client_session(
                base_endpoint, orgs, verify_tls, self.settings) as session:
            url = "{}{}".format(session.base_url, url)
            try:
                with remove_sensitive_extension_values(
                        self.experiment, ["experiment_path"]):
                    r = session.request(method=method, url=url, **kwargs)
                    return r
            except Exception as x:
                logger.debug(
                    "Error when calling URL '{}'".format(url), exc_info=True)
                logger.error(
                    "Failed to call ChaosIQ's services, please contact their "
                    "support with the `./chaostoolkit.log` file: {}".format(
                        str(x)
                    )
                )

    def started(self, experiment: Experiment, journal: Journal) -> None:
        """
        Notify the ChaosIQ service the verification has now started.

        Provide it with the current journal and status.
        """
        self._start_time = datetime.now()
        base_endpoint, verify_tls, orgs = get_call_context(self.settings)
        with client_session(
                base_endpoint, orgs, verify_tls, self.settings) as session:
            r = initialize_execution(session, experiment, journal)
            if r.status_code not in [200, 201]:
                raise InterruptExecution(
                    "It is possible you are trying to run a verification "
                    "against a team that is not the active team of the `chaos` "  # noqa: E501
                    "session. Please run `chaos team` to switch active team "
                    "then try again. If the problem persists or the team is "
                    "the correct one, please contact the ChaosIQ support.")
            payload = r.json()
            execution_id = payload["id"]

        r = self._make_call(
            "POST", self.verification_run_path, json={
                "journal": journal,
                "status": "started",
                "experiment_id": get_experiment_id(experiment),
                "execution_id": execution_id
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run was started: {}".format(
                    error))
            return

        payload = r.json()
        self.run_id = payload["id"]
        if self.run_id:
            logger.debug("Verification run '{}' started".format(self.run_id))
            set_run_id(self.run_id, experiment)

    def finish(self, journal: Journal) -> None:
        """
        Notify the ChaosIQ service the verification has finished.
        """
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-completed",
                "payload": journal
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run was finished: {}".format(
                    error))

        successful_samples = 0
        deviated_samples = 0
        total_number_of_samples = 0
        not_run_samples = 0
        measurements = journal.get("steady_states", {}).get("during", [])
        # TODO: replace with steady_states.during server side
        journal["measurements"] = measurements
        for m in measurements:
            total_number_of_samples = total_number_of_samples + 1
            ssm = m.get("steady_state_met")
            if ssm is False:
                deviated_samples = deviated_samples + 1
            elif ssm is True:
                successful_samples = successful_samples + 1
            else:
                not_run_samples = not_run_samples + 1

        r = self._make_call(
            "POST", "{}/{}/finished".format(
                self.verification_run_path, self.run_id), json={
                "journal": journal,
                "status": journal.get("status", "unknown"),
                "results": {
                    "successful_samples": successful_samples,
                    "deviated_samples": deviated_samples,
                    "not_run_samples": not_run_samples,
                    "total_number_of_samples": total_number_of_samples,
                    "total_duration": (
                        datetime.now() - self._start_time).total_seconds()
                }
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run was finished: {}".format(
                    error))

    def interrupted(self, experiment: Experiment,
                    journal: Journal) -> None:
        """
        Notify the ChaosIQ service the verification was interrupted by an
        `InterruptedExecution`.
        """
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-interrupted"
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run was interrupted: {}".format(
                    error))

    def signal_exit(self) -> None:
        """
        Notify the ChaosIQ service the verification was exited by a signal.
        """
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-exited-by-signal"
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run was exited by "
                "signal: {}".format(error))

    def start_continous_hypothesis(self, frequency: int) -> None:
        """
        Notify the ChaosIQ service the continuous verification has started.
        """
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-sample-started",
                "payload": {
                    "frequency": frequency
                }
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run has started sampling the "
                "system: {}".format(error))

    def continous_hypothesis_iteration(self, iteration_index: int,
                                       state: Any) -> None:
        """
        Notify the ChaosIQ service of a single continuous verification
        iteration.
        """
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-sample",
                "payload": {
                    "iteration": iteration_index,
                    "state": state
                }
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run of new sample of the "
                "system: {}".format(error))

    def continous_hypothesis_completed(self, experiment: Experiment,
                                       journal: Journal,
                                       exception: Exception = None) -> None:
        """
        Notify the ChaosIQ service the continuous verification has ended.
        """
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-sampling-completed"
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run has completed sampling the "
                "system: {}".format(error))

    def start_hypothesis_before(self, experiment: Experiment) -> None:
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-hypothesis-before-method-started"
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run hypothesis before "
                "method started: {}".format(error))

    def hypothesis_before_completed(self, experiment: Experiment,
                                    state: Dict[str, Any],
                                    journal: Journal) -> None:
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-hypothesis-before-method-completed"
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run hypothesis before "
                "method completed: {}".format(error))

    def start_hypothesis_after(self, experiment: Experiment) -> None:
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-hypothesis-after-method-started"
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run hypothesis after "
                "method started: {}".format(error))

    def hypothesis_after_completed(self, experiment: Experiment,
                                   state: Dict[str, Any],
                                   journal: Journal) -> None:
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-hypothesis-after-method-completed"
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run hypothesis after "
                "method completed: {}".format(error))

    def start_method(self, experiment: Experiment) -> None:
        """
        Notify the ChaosIQ service the method has started
        """
        if not self.initialized:
            return

        warm_up_duration = self.verification.get("warm-up-duration")
        logger.info(
            "Starting verification warm-up period of {} "
            "seconds".format(warm_up_duration))
        if warm_up_duration:
            time.sleep(warm_up_duration)
        logger.info("Finished verification warm-up")

        logger.info("Triggering verification conditions")

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-condition-started",
                "payload": {}
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run condition has started "
                ": {}".format(error))

    def method_completed(self, experiment: Experiment, state: Any) -> None:
        """
        Notify the ChaosIQ service the method has ended
        """
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-condition-completed",
                "payload": {
                    "state": state
                }
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run condition has completed "
                ": {}".format(error))

        duration_of_conditions = self.verification.get(
            "duration-of-conditions")
        logger.info("Starting verification conditions for {} seconds"
                    .format(duration_of_conditions))
        if duration_of_conditions:
            time.sleep(duration_of_conditions)
        logger.info("Finished verification conditions duration")

    def start_rollbacks(self, experiment: Experiment) -> None:
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-rollbacks-started"
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification rollbacks "
                "started: {}".format(error))

    def rollbacks_completed(self, experiment: Experiment,
                            journal: Journal) -> None:
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-rollbacks-completed"
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run rollbacks "
                "completed: {}".format(error))

    def start_cooldown(self, duration: int) -> None:
        """
        Notify the ChaosIQ service the cooldown perios has started
        """
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-cooldown-started",
                "payload": {
                    "duration": duration
                }
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run cooldown has started "
                ": {}".format(error))

        cool_down_duration = self.verification.get("cool-down-duration")
        logger.info(
            "Starting verification cool-down period of "
            "{} seconds".format(cool_down_duration))
        if cool_down_duration:
            time.sleep(cool_down_duration)
        logger.info("Finished verification cool-down period")

    def cooldown_completed(self) -> None:
        """
        Notify the ChaosIQ service the cooldown perios has ended
        """
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-cooldown-completed"
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run cooldown has completed "
                ": {}".format(error))
