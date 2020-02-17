# -*- coding: utf-8 -*-
from contextlib import contextmanager
from datetime import datetime
from typing import Any, NoReturn, Optional, Tuple

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

__all__ = ["verification_run", "VerificationRunEventHandler", "get_run_id"]


@contextmanager
def verification_run(experiment: Experiment, settings: Settings):
    handler = VerificationRunEventHandler(experiment, settings)
    yield handler
    handler.bye()


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


def set_run_id(verification_run_id: str, experiment: Experiment) -> NoReturn:
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
    def __init__(self, experiment: Experiment, settings: Settings):
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
    def initialized(self):
        return self.run_id is not None

    def bye(self):
        pass

    @property
    def verification_run_path(self):
        return urls.verification_run(
            urls.verification(
                "", verification_id=self.verification_id
            )
        )

    @property
    def verification_run_event_path(self):
        return urls.verification_run_events(
            urls.verification_run(
                urls.verification(
                    "", verification_id=self.verification_id
                ),
                verification_run_id=self.run_id
            )
        )

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

    def start(self, journal: Journal) -> str:
        self._start_time = datetime.now()
        base_endpoint, verify_tls, orgs = get_call_context(self.settings)
        with client_session(
                base_endpoint, orgs, verify_tls, self.settings) as session:
            r = initialize_execution(session, self.experiment, journal)
            if r.status_code not in [200, 201]:
                raise InterruptExecution(
                    "It is possible you are trying to run a verification "
                    "against a team that is not the active team of the `chaos`"
                    "session. Please run `chaos team` to switch active team "
                    "then try again. If the problem persists or the team is "
                    "the correct one, please contact the ChaosIQ support.")
            payload = r.json()
            execution_id = payload["id"]

        r = self._make_call(
            "POST", self.verification_run_path, json={
                "journal": journal,
                "status": "started",
                "experiment_id": get_experiment_id(self.experiment),
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
            set_run_id(self.run_id, self.experiment)
        return self.run_id

    def finish(self, journal: Journal) -> NoReturn:
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
        for m in journal.get("measurements", []):
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
                "status": "completed",
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

    def interrupt(self) -> NoReturn:
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

    def signal_exit(self) -> NoReturn:
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

    def start_measurements(self, frequency: int) -> NoReturn:
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

    def measurement_sample(self, iteration_index: int, state: Any) -> NoReturn:
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

    def measurements_completed(self) -> NoReturn:
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

    def start_condition(self, iteration_index: int = 0) -> NoReturn:
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-condition-started",
                "payload": {
                    "iteration": iteration_index
                }
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run condition has started "
                ": {}".format(error))

    def condition_completed(self, state: Any,
                            iteration_index: int = 0) -> NoReturn:
        if not self.initialized:
            return

        r = self._make_call(
            "POST", self.verification_run_event_path, json={
                "category": "verification-condition-completed",
                "payload": {
                    "iteration": iteration_index
                }
            })
        error = self.get_error(r)
        if error or (r is None):
            logger.error(
                "Failed to notify verification run condition has completed "
                ": {}".format(error))

    def start_cooldown(self, duration: int) -> NoReturn:
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

    def cooldown_completed(self) -> NoReturn:
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
