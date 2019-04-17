# -*- coding: utf-8 -*-
from chaoslib.types import Journal
from logzero import logger
import requests

from . import Context

__all__ = ["publish"]


def build_base_url(base_url: str) -> str:
    """
    Build the base URL of our API endpoint
    """
    return '/'.join([base_url, 'api', 'v1'])


def build_experiment_url(base_url: str) -> str:
    """
    Build the URL for an experiment to be published to.
    """
    return '/'.join([base_url, 'experiments'])


def build_run_url(base_url: str) -> str:
    """
    Build the URL for a journal to be pushed to.
    """
    return '/'.join([base_url, 'executions'])


def publish(context: Context, journal_path: str, journal: Journal):
    """
    Publish the experiment and the journal to ChaosIQ
    """
    if not context.url or not context.token:
        logger.debug(
            "No ChaosIQ configured. Please execute `chaosiq login` before "
            "attempting to publish.")
        return

    headers = {
        "Accept": "application/json",
        "Authorization": "Bearer {}".format(context.token)
    }
    url = build_base_url(context.url)

    experiment_url = build_experiment_url(url)
    logger.debug(
        "Publishing experiment to ChaosIQ at {}".format(
            experiment_url))

    experiment = journal["experiment"]
    r = requests.post(
        experiment_url, headers=headers, json=experiment)

    # we will receive a 201 only when the experiment was indeed created
    # otherwise, it means it already exists
    if r.status_code not in [200, 201]:
        is_json = 'application/json' in r.headers["content-type"]
        error = r.json() if is_json else r.text
        logger.warning(
            "Experiment failed to be published to {}: {}".format(url, error))
    else:
        logger.info("Experiment available at {}".format(
            r.headers["Location"]))

        url = build_run_url(url)
        logger.debug("Publishing journal to ChaosIQ at {}".format(url))
        r = requests.post(url, headers=headers, json=journal)

        if r.status_code != 201:
            logger.debug(r.text)
            logger.warning(
                "Experimental findings in '{}' failed to publish".format(
                    journal_path))
        else:
            logger.info(
                "Experimental findings in '{}' published to {}".format(
                    journal_path, r.headers["Location"]))
