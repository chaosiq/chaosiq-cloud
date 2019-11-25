# -*- coding: utf-8 -*-
from copy import deepcopy
import threading

from typing import List, NoReturn

from chaoslib.exceptions import InterruptExecution
from chaoslib.types import Extension, Journal
import requests

from . import urls, get_chaosiq_extension_from_journal, get_execution_id, \
    get_experiment_id


__all__ = ["is_allowed_to_continue", "set_applied_safeguards_for_execution"]
safeguards_state = {}
state_lock = threading.Lock()


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

    safeguards_url = urls.safeguard(urls.execution(
        urls.experiment(session.base_url, experiment_id=experiment_id),
        execution_id=execution_id))
    r = session.get(safeguards_url)
    if r.status_code > 399:
        return

    state = r.json()
    if state.get("allowed", True) is False:
        safeguards = "\n".join([p["name"] for p in state.get("policies")])
        with state_lock:
            safeguards_state[execution_id] = deepcopy(state.get("policies"))

        raise InterruptExecution(
            "The following safe guards disallow this execution from "
            "continuing:\n{}".format(safeguards)
        )


def set_applied_safeguards_for_execution(extensions: List[Extension],
                                         journal: Journal):
    """
    Set the list of safeguards applied to an execution's journal.
    """
    execution_id = get_execution_id(extensions)
    extension = get_chaosiq_extension_from_journal(journal)
    with state_lock:
        extension["safeguards"] = safeguards_state.get(execution_id)
