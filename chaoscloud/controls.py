# -*- coding: utf-8 -*-
from typing import Any, Dict, List, NoReturn
from urllib.parse import urlsplit, urlunsplit

from chaoslib.experiment import initialize_run_journal
from chaoslib.types import Activity, Configuration, Extension, \
    Experiment, Hypothesis, Journal, Run, Secrets, Settings
from logzero import logger

from .api import client_session
from .api.experiment import publish_experiment
from .api.execution import initialize_execution, publish_event, \
    publish_execution, save_ids_to_journal
from .api.safeguard import is_allowed_to_continue, \
    set_applied_safeguards_for_execution
from .settings import is_feature_enabled
from .sig import register_cleanup_on_forced_exit

Organizations = List[Dict[str, Any]]


def configure_control(experiment: Experiment, settings: Settings,
                      configuration: Configuration = None,
                      secrets: Secrets = None, url: str = None,
                      verify_tls: bool = True,
                      organizations: Organizations = None) -> NoReturn:
    """
    Initialize the execution's journal and publish both the experiment
    and the journal.
    """
    register_cleanup_on_forced_exit()

    if not is_feature_enabled(settings, "publish"):
        logger.warning(
            "\nChaosIQ extension has disabled publishing\n"
            "which essentially disables the extension entirely.\n"
            "Run `chaos enable publish` to activate the extension again.")
        return

    journal = initialize_run_journal(experiment)
    with client_session(url, organizations, verify_tls, settings) as session:
        publish_experiment(session, experiment)
        initialize_execution(session, experiment, journal)


def after_loading_experiment_control(context: str, state: Experiment, *,
                                     url: str, verify_tls: bool = False,
                                     organizations: Organizations = None) \
                                         -> NoReturn:
    """
    Inject the source of the experiment, when it is a URL, into the experiment
    so we can determine if that experiment had already been seen in that
    organization. If so, we can add the execution to that existing experiment.

    We do not send any username/password/token found in the network location
    part of the source, if it's an URL. It is stripped out before being sent.
    """
    parsed = urlsplit(context)
    if parsed.scheme.lower() not in ('http', 'https'):
        # probably not even a url, maybe a local path
        return

    dup = list(parsed)
    # we do not want to track sensitive data such as username/password/tokens
    if parsed.username or parsed.password:
        dup[1] = parsed.hostname
        context = urlunsplit(dup)

    extensions = state.setdefault("extensions", [])
    for extension in extensions:
        if extension["name"] == "chaosiq":
            extension["source"] = context
            break
    else:
        extensions.append({
            "name": "chaosiq",
            "source": context
        })


def before_experiment_control(context: Experiment,
                              configuration: Configuration = None,
                              secrets: Secrets = None,
                              settings: Settings = None,
                              extensions: List[Extension] = None,
                              *, url: str,
                              verify_tls: bool = False,
                              organizations: Organizations = None) \
                                  -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "starting-experiment", context, configuration, secrets,
            extensions, settings)
        if not is_feature_enabled(settings, "safeguards"):
            logger.warning(
                "\nChaosIQ extension has disabled checking for runtime "
                "safe guards.\n"
                "Run `chaos enable safeguards` to activate them again.")
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
                             organizations: Organizations = None) \
                                 -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    save_ids_to_journal(extensions, state)
    set_applied_safeguards_for_execution(extensions, state)
    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "experiment-finished", context, configuration, secrets,
            extensions, settings, state)
        publish_execution(session, state)


def before_hypothesis_control(context: Hypothesis,
                              configuration: Configuration = None,
                              secrets: Secrets = None,
                              settings: Settings = None,
                              extensions: List[Extension] = None,
                              *, url: str,
                              verify_tls: bool = False,
                              organizations: Organizations = None) \
                                  -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "starting-hypothesis", context, configuration, secrets,
            extensions, settings)

        if is_feature_enabled(settings, "safeguards"):
            is_allowed_to_continue(session, extensions)


def after_hypothesis_control(context: Hypothesis,
                             state: Dict[str, Any],
                             configuration: Configuration = None,
                             secrets: Secrets = None,
                             settings: Settings = None,
                             extensions: List[Extension] = None,
                             *, url: str,
                             verify_tls: bool = False,
                             organizations: Organizations = None) \
                                 -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "hypothesis-finished", context, configuration, secrets,
            extensions, settings, state)
        if is_feature_enabled(settings, "safeguards"):
            is_allowed_to_continue(session, extensions)


def before_method_control(context: Experiment,
                          configuration: Configuration = None,
                          secrets: Secrets = None,
                          settings: Settings = None,
                          extensions: List[Extension] = None,
                          *, url: str, verify_tls: bool = False,
                          organizations: Organizations = None) \
                              -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "starting-method", context, configuration, secrets,
            extensions, settings)
        if is_feature_enabled(settings, "safeguards"):
            is_allowed_to_continue(session, extensions)


def after_method_control(context: Experiment,
                         state: List[Run], configuration: Configuration = None,
                         secrets: Secrets = None,
                         settings: Settings = None,
                         extensions: List[Extension] = None,
                         *, url: str, verify_tls: bool = False,
                         organizations: Organizations = None) \
                             -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "method-finished", context, configuration, secrets,
            extensions, settings, state)

        if is_feature_enabled(settings, "safeguards"):
            is_allowed_to_continue(session, extensions)


def before_rollback_control(context: Experiment,
                            configuration: Configuration = None,
                            secrets: Secrets = None,
                            settings: Settings = None,
                            extensions: List[Extension] = None,
                            *, url: str, verify_tls: bool = False,
                            organizations: Organizations = None) \
                                -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "starting-rollback", context, configuration, secrets,
            extensions, settings)

        if is_feature_enabled(settings, "safeguards"):
            is_allowed_to_continue(session, extensions)


def after_rollback_control(context: Experiment,
                           state: List[Run],
                           configuration: Configuration = None,
                           secrets: Secrets = None,
                           settings: Settings = None,
                           extensions: List[Extension] = None,
                           *, url: str, verify_tls: bool = False,
                           organizations: Organizations = None) \
                               -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "rollback-finished", context, configuration, secrets,
            extensions, settings, state)

        if is_feature_enabled(settings, "safeguards"):
            is_allowed_to_continue(session, extensions)


def before_activity_control(context: Activity,
                            configuration: Configuration = None,
                            secrets: Secrets = None,
                            settings: Settings = None,
                            extensions: List[Extension] = None,
                            *, url: str, verify_tls: bool = False,
                            organizations: Organizations = None) \
                                -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "starting-activity", context, configuration, secrets,
            extensions, settings)

        if is_feature_enabled(settings, "safeguards"):
            is_allowed_to_continue(session, extensions)


def after_activity_control(context: Activity, state: Run,
                           configuration: Configuration = None,
                           secrets: Secrets = None,
                           settings: Settings = None,
                           extensions: List[Extension] = None,
                           *, url: str, verify_tls: bool = False,
                           organizations: Organizations = None) \
                               -> NoReturn:
    if not is_feature_enabled(settings, "publish"):
        return

    with client_session(url, organizations, verify_tls, settings) as session:
        publish_event(
            session, "activity-finished", context, configuration, secrets,
            extensions, settings, state)

        if is_feature_enabled(settings, "safeguards"):
            is_allowed_to_continue(session, extensions)
