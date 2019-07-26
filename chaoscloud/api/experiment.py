# -*- coding: utf-8 -*-
from typing import NoReturn, Optional

from chaoslib.types import Experiment
from logzero import logger
import requests

from . import urls

__all__ = ["publish_experiment"]


def publish_experiment(session: requests.Session,
                       experiment: Experiment) -> Optional[requests.Response]:
    """
    Publish the experiment.
    """
    try:
        experiment_url = urls.experiment(session.base_url)
        r = session.post(experiment_url, json={
            "experiment": experiment
        })
    except Exception:
        logger.warning(
            "Failed to publish experiment to '{}'".format(experiment_url))
        logger.debug("Failed to publish the experiment", exc_info=True)
        return

    if r.status_code > 399:
        is_json = 'application/json' in r.headers.get("content-type", '')
        error = r.json() if is_json else r.text
        logger.warning("Experiment failed to be published: {}".format(error))
    elif r.status_code == 204:
        logger.debug("Experiment has not changed since it was created")
        return r
    else:
        payload = r.json()
        set_experiment_id(payload["id"], experiment)

    return r


###############################################################################
# Internals
###############################################################################
def get_experiment_id(experiment: Experiment) -> str:
    extensions = experiment.get("extensions", [])
    for extension in extensions:
        if extension["name"] == "chaosiq":
            return extension["experiment_id"]


def set_experiment_id(experiment_id: str, experiment: Experiment) -> NoReturn:
    extensions = experiment.setdefault("extensions", [])
    for extension in extensions:
        if extension["name"] == "chaosiq":
            extension["experiment_id"] = experiment_id
            break
    else:
        extensions.append({
            "name": "chaosiq",
            "experiment_id": experiment_id
        })
