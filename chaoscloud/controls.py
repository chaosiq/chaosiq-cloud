# -*- coding: utf-8 -*-
import os
from typing import Any, Dict, List, NoReturn
from urllib.parse import urlsplit, urlunsplit

from chaoslib.experiment import initialize_run_journal
from chaoslib.types import (Activity, Configuration, Experiment, Extension,
                            Hypothesis, Journal, Run, Secrets, Settings)
from logzero import logger

from .api import client_session
from .api.execution import (initialize_execution, publish_event,
                            publish_execution, save_ids_to_journal)
from .api.experiment import publish_experiment
from .api.safeguard import (is_allowed_to_continue,
                            set_applied_safeguards_for_execution)
from .api.verification import get_run_id
from .extension import remove_sensitive_extension_values, set_extension_value
from .settings import is_feature_enabled
from .sig import register_cleanup_on_forced_exit
from .types import Organizations
from .workspace import (get_experiment_metadata_from_workspace,
                        initialize_workspace_path, load_workspace,
                        register_experiment_to_workspace, save_workspace)


def configure_control(experiment: Experiment, settings: Settings,
                      configuration: Configuration = None,
                      secrets: Secrets = None, url: str = None,
                      verify_tls: bool = True,
                      organizations: Organizations = None) -> NoReturn:
    """
    Initialize the execution's journal and publish both the experiment
    and the journal.
    Updates the ChaosIQ workspace for local files experiments.
    """
    register_cleanup_on_forced_exit()

    if not is_feature_enabled(settings, "publish"):
        logger.warning(
            "\nChaosIQ extension has disabled publishing\n"
            "which essentially disables the extension entirely.\n"
            "Run `chaos enable publish` to activate the extension again.")
        return

    is_in_verification = get_run_id(experiment) is not None
    # when running a verification the experiment/execution have been
    # initialized already
    if not is_in_verification:
        with remove_sensitive_extension_values(
                experiment, ["experiment_path"]):
            journal = initialize_run_journal(experiment)

        with client_session(url, organizations, verify_tls, settings) as \
                session:
            publish_experiment(session, experiment)
            initialize_execution(session, experiment, journal)

    if is_feature_enabled(settings, "workspace"):
        register_experiment_to_workspace(experiment, organizations)
        save_workspace()


def before_loading_experiment_control(context: str, state: Experiment,
                                      settings: Settings = None,
                                      *, url: str, verify_tls: bool = False,
                                      organizations: Organizations = None) \
                                          -> NoReturn:
    """
    Ensure the ChaosIQ workspace sub-folder exists for the folder
    containing the experiment loaded from the local file system.
    """
    if not os.path.exists(context):
        return

    if is_feature_enabled(settings, "workspace"):
        initialize_workspace_path(context)
        load_workspace()


def after_loading_experiment_control(context: str, state: Experiment,
                                     settings: Settings = None,
                                     *, url: str, verify_tls: bool = False,
                                     organizations: Organizations = None) \
                                         -> NoReturn:
    """
    Inject the source of the experiment, when it is a URL, into the experiment
    so we can determine if that experiment had already been seen in that
    organization. If so, we can add the execution to that existing experiment.

    We do not send any username/password/token found in the network location
    part of the source, if it's an URL. It is stripped out before being sent.

    In case the experimentation is a valid path on the local file system,
    once loaded, we need to check whether this is a new experiment
    or one that is already known (previously run) ie that has an
    experiment ID stored in the workspace associated to the local path.
    If so, we set another plugin key `experiment_path` within the experiment.

    NB: For local files, we can NOT use the source as this does not work
    when two users publish experiments from their own machine, with the same
    path, as it would be recognized as the same experiment, which might not be!

    Source is supposed to be unique for any user within the same organization
    """
    if os.path.exists(context) and is_feature_enabled(settings, "workspace"):
        meta = get_experiment_metadata_from_workspace(
            state, organizations, context)
        experiment_id = meta.get("experiment_id") if meta else None
        if experiment_id:
            # this is a known experiment, update it with its ID from workspace
            logger.debug(
                "Using experiment ID {id} from workspace "
                "for experiment at location {path}".format(
                    id=experiment_id, path=context))
            set_extension_value(state, "experiment_id", experiment_id)
        else:
            # here this is the first time we uses this experiment path,
            # hence register it for later use after the experiment has been
            # published so that we can link the path and the API generated ID
            set_extension_value(state, "experiment_path", context)

    parsed = urlsplit(context)
    if parsed.scheme.lower() in ('http', 'https'):
        dup = list(parsed)
        # we do not want to track sensitive data such as username/password/tokens  # noqa: E501
        if parsed.username or parsed.password:
            dup[1] = parsed.hostname
            context = urlunsplit(dup)

        set_extension_value(state, "source", context)


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
