# -*- coding: utf-8 -*-
from typing import List, NoReturn, Optional

from chaoslib.exceptions import InterruptExecution
from chaoslib.types import Extension
import requests

from . import urls


__all__ = ["is_allowed_to_continue"]


def is_allowed_to_continue(session: requests.Session,
                           extensions: List[Extension]) -> NoReturn:
    """
    Query the runtime policy and return a boolean indicating if the execution
    may carry on or not.
    """
    experiment_id = get_experiment_id(extensions)
    if not experiment_id:
        return

    execution_id = get_execution_id(extensions)
    if not execution_id:
        return

    policies_url = urls.policy(urls.execution(
        urls.experiment(session.base_url, experiment_id=experiment_id),
        execution_id=execution_id))
    r = session.get(policies_url)
    if r.status_code > 399:
        return

    state = r.json()
    if state.get("allowed", True) is False:
        policies = "\n".join([p["name"] for p in state.get("policies")])
        raise InterruptExecution(
            f"This experiment was interrupted due to policies:\n{policies}"
        )


###############################################################################
# Internals
###############################################################################
def get_experiment_id(extensions: List[Extension]) -> Optional[str]:
    if not extensions:
        return
    for extension in extensions:
        if extension["name"] == "chaosiq":
            return extension["experiment_id"]


def get_execution_id(extensions: List[Extension]) -> Optional[str]:
    for extension in extensions:
        if extension["name"] == "chaosiq":
            return extension["execution_id"]
