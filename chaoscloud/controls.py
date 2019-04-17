# -*- coding: utf-8 -*-
from typing import Any, Dict, List, NoReturn

from chaoslib.experiment import initialize_run_journal
from chaoslib.types import Activity, Configuration, Extension, \
    Experiment, Hypothesis, Journal, Run, Secrets, Settings
from logzero import logger

from .api import client_session
from .api.experiment import publish_experiment
from .api.execution import initialize_execution, publish_event, \
    publish_execution
from .api.policy import is_allowed_to_continue
from .settings import is_feature_enabled


def configure_control(experiment: Experiment, settings: Settings,
                      configuration: Configuration = None,
                      secrets: Secrets = None, url: str = None,
                      verify_tls: bool = True,
                      organizations: List[Dict[str, Any]] = None) -> NoReturn:
    """
    Initialize the execution's journal and publish both the experiment
    and the journal.
    """
    if not is_feature_enabled(settings, "publish"):
        logger.warning(
            "\nChaos Toolkit extension has disabled publishing\n"
            "which essentially disables the extension entirely.\n"
            "Run `chaos enable publish` to activate the extension again.")
        return

    journal = initialize_run_journal(experiment)
    with client_session(url, organizations, verify_tls, settings) as session:
        publish_experiment(session, experiment)
        initialize_execution(session, experiment, journal)


def before_experiment_control(context: Experiment,
                              configuration: Configuration = None,
                              secrets: Secrets = None,
                              settings: Settings = None,
                              extensions: List[Extension] = None,
                              *, url: str,
                              verify_tls: bool = False,
                              organizations: List[Dict[str, Any]] = None) \
                                  -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "starting-experiment", context, configuration, secrets,
            extensions, settings)
        if not is_feature_enabled(settings, "policies"):
            logger.warning(
                "\nChaos Toolkit extension has disabled checking for runtime "
                "policies.\n"
                "Run `chaos enable policies` to activate them again.")
        else:
            is_allowed_to_continue(session, extensions)


def after_experiment_control(context: Experiment,
                             state: Journal,
                             configuration: Configuration = None,
                             secrets: Secrets = None,
                             settings: Settings = None,
                             extensions: List[Extension] = None,
                             *, url: str,
                             verify_tls: bool = False,
                             organizations: List[Dict[str, Any]] = None) \
                                 -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "experiment-finished", context, configuration, secrets,
            extensions, settings, state)
        publish_execution(session, state)
        if is_feature_enabled(settings, "policies"):
            is_allowed_to_continue(session, extensions)


def before_hypothesis_control(context: Hypothesis,
                              configuration: Configuration = None,
                              secrets: Secrets = None,
                              settings: Settings = None,
                              extensions: List[Extension] = None,
                              *, url: str,
                              verify_tls: bool = False,
                              organizations: List[Dict[str, Any]] = None) \
                                  -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "starting-hypothesis", context, configuration, secrets,
            extensions, settings)
        if is_feature_enabled(settings, "policies"):
            is_allowed_to_continue(session, extensions)


def after_hypothesis_control(context: Hypothesis,
                             state: Dict[str, Any],
                             configuration: Configuration = None,
                             secrets: Secrets = None,
                             settings: Settings = None,
                             extensions: List[Extension] = None,
                             *, url: str,
                             verify_tls: bool = False,
                             organizations: List[Dict[str, Any]] = None) \
                                 -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "hypothesis-finished", context, configuration, secrets,
            extensions, settings, state)
        if is_feature_enabled(settings, "policies"):
            is_allowed_to_continue(session, extensions)


def before_method_control(context: Experiment,
                          configuration: Configuration = None,
                          secrets: Secrets = None,
                          settings: Settings = None,
                          extensions: List[Extension] = None,
                          *, url: str, verify_tls: bool = False,
                          organizations: List[Dict[str, Any]] = None) \
                              -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "starting-method", context, configuration, secrets,
            extensions, settings)
        if is_feature_enabled(settings, "policies"):
            is_allowed_to_continue(session, extensions)


def after_method_control(context: Experiment,
                         state: List[Run], configuration: Configuration = None,
                         secrets: Secrets = None,
                         settings: Settings = None,
                         extensions: List[Extension] = None,
                         *, url: str, verify_tls: bool = False,
                         organizations: List[Dict[str, Any]] = None) \
                             -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "method-finished", context, configuration, secrets,
            extensions, settings, state)

        if is_feature_enabled(settings, "policies"):
            is_allowed_to_continue(session, extensions)


def before_rollback_control(context: Experiment,
                            configuration: Configuration = None,
                            secrets: Secrets = None,
                            settings: Settings = None,
                            extensions: List[Extension] = None,
                            *, url: str, verify_tls: bool = False,
                            organizations: List[Dict[str, Any]] = None) \
                                -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "starting-rollback", context, configuration, secrets,
            extensions, settings)

        if is_feature_enabled(settings, "policies"):
            is_allowed_to_continue(session, extensions)


def after_rollback_control(context: Experiment,
                           state: List[Run],
                           configuration: Configuration = None,
                           secrets: Secrets = None,
                           settings: Settings = None,
                           extensions: List[Extension] = None,
                           *, url: str, verify_tls: bool = False,
                           organizations: List[Dict[str, Any]] = None) \
                               -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "rollback-finished", context, configuration, secrets,
            extensions, settings, state)

        if is_feature_enabled(settings, "policies"):
            is_allowed_to_continue(session, extensions)


def before_activity_control(context: Activity,
                            configuration: Configuration = None,
                            secrets: Secrets = None,
                            settings: Settings = None,
                            extensions: List[Extension] = None,
                            *, url: str, verify_tls: bool = False,
                            organizations: List[Dict[str, Any]] = None) \
                                -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "starting-activity", context, configuration, secrets,
            extensions, settings)

        if is_feature_enabled(settings, "policies"):
            is_allowed_to_continue(session, extensions)


def after_activity_control(context: Activity, state: Run,
                           configuration: Configuration = None,
                           secrets: Secrets = None,
                           settings: Settings = None,
                           extensions: List[Extension] = None,
                           *, url: str, verify_tls: bool = False,
                           organizations: List[Dict[str, Any]] = None) \
                               -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "activity-finished", context, configuration, secrets,
            extensions, settings, state)

        if is_feature_enabled(settings, "policies"):
            is_allowed_to_continue(session, extensions)
