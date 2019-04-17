from datetime import datetime
from typing import Any, Dict, List, NoReturn
import uuid

from chaoslib.experiment import initialize_run_journal
from chaoslib.types import Activity, Configuration, Extension, \
    Experiment, Hypothesis, Journal, Run, Secrets, Settings
from cloudevents.sdk import converters
from cloudevents.sdk import marshaller
from cloudevents.sdk.converters import structured
from cloudevents.sdk.event import v02
from logzero import logger
import simplejson as json
import requests
from tzlocal import get_localzone


def before_experiment_control(context: Experiment,
                              configuration: Configuration = None,
                              secrets: Secrets = None,
                              settings: Settings = None,
                              extensions: List[Extension] = None):
    # first we create a new execution and we track its id in the experiment
    token = get_access_token(settings)
    base_url = get_service_url(settings)
    journal = initialize_run_journal(context)

    url = f"{base_url}/api/v1/executions"
    r = requests.post(
        url, headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Connection": "close"
        },
        json=journal
    )
    if r.status_code != 201:
        logger.debug(f"Failed to create execution: {r.text}")
        return

    execution = r.json()
    set_execution_id_in_extension(execution["id"], context, extensions)
    extensions = context.get("extensions")

    send_event(
        "starting-experiment", context, configuration, secrets, extensions,
        settings)


def after_experiment_control(context: Experiment,
                             state: Journal,
                             configuration: Configuration = None,
                             secrets: Secrets = None,
                             settings: Settings = None,
                             extensions: List[Extension] = None):
    send_event(
        "experiment-finished", context, configuration, secrets, extensions,
        settings, state)


def before_hypothesis_control(context: Hypothesis,
                              configuration: Configuration = None,
                              secrets: Secrets = None,
                              settings: Settings = None,
                              extensions: List[Extension] = None):
    send_event(
        "starting-hypothesis", context, configuration, secrets, extensions,
        settings)


def after_hypothesis_control(context: Hypothesis,
                             state: Dict[str, Any],
                             configuration: Configuration = None,
                             secrets: Secrets = None,
                             settings: Settings = None,
                             extensions: List[Extension] = None):
    send_event(
        "hypothesis-finished", context, configuration, secrets, extensions,
        settings, state)


def before_method_control(context: Experiment,
                          configuration: Configuration = None,
                          secrets: Secrets = None,
                          settings: Settings = None,
                          extensions: List[Extension] = None):
    send_event(
        "starting-method", context, configuration, secrets, extensions,
        settings)


def after_method_control(context: Experiment,
                         state: List[Run], configuration: Configuration = None,
                         secrets: Secrets = None,
                         settings: Settings = None,
                         extensions: List[Extension] = None):
    send_event(
        "method-finished", context, configuration, secrets, extensions,
        settings, state)


def before_rollback_control(context: Experiment,
                            configuration: Configuration = None,
                            secrets: Secrets = None,
                            settings: Settings = None,
                            extensions: List[Extension] = None):
    send_event(
        "starting-rollback", context, configuration, secrets, extensions,
        settings)


def after_rollback_control(context: Experiment,
                           state: List[Run],
                           configuration: Configuration = None,
                           secrets: Secrets = None,
                           settings: Settings = None,
                           extensions: List[Extension] = None):
    send_event(
        "rollback-finished", context, configuration, secrets, extensions,
        settings, state)


def before_activity_control(context: Activity,
                            configuration: Configuration = None,
                            secrets: Secrets = None,
                            settings: Settings = None,
                            extensions: List[Extension] = None):
    send_event(
        "starting-activity", context, configuration, secrets, extensions,
        settings)


def after_activity_control(context: Activity, state: Run,
                           configuration: Configuration = None,
                           secrets: Secrets = None,
                           settings: Settings = None,
                           extensions: List[Extension] = None):
    send_event(
        "activity-finished", context, configuration, secrets, extensions,
        settings, state)


###############################################################################
# Internals
###############################################################################
def send_event(event_type: str, payload: Any,
               configuration: Configuration, secrets: Secrets,
               extensions: List[Extension], settings: Settings,
               state: Any = None) -> NoReturn:
    token = get_access_token(settings)
    base_url = get_service_url(settings)

    execution_id = get_execution_id_from_extension(extensions)
    if not execution_id:
        logger.debug("Cannot send event to ChaosIQ")
        return

    tz = get_localzone()
    url = f"{base_url}/api/v1/executions/{execution_id}/events"

    data = {
        "context": payload,
        "state": state
    }
    event = (
        v02.Event().
        SetContentType("application/json").
        SetData(json.dumps(data)).
        SetEventID(str(uuid.uuid4())).
        SetSource("chaosiq-chaostoolkit-plugin").
        SetEventTime(tz.localize(datetime.now()).isoformat()).
        SetEventType(event_type)
    )
    m = marshaller.NewHTTPMarshaller(
        [
            structured.NewJSONHTTPCloudEventConverter()
        ]
    )

    headers, body = m.ToRequest(event, converters.TypeStructured, lambda x: x)
    headers["Authorization"] = f"Bearer {token}"

    r = requests.post(
        url, headers=headers,
        data=body.getvalue()
    )
    if r.status_code != 201:
        logger.debug(f"Failed to push event to {url}: {r.text}")


def get_access_token(settings: Settings) -> str:
    chaosiq_settings = settings.get("vendor", {}).get("chaosiq", {})
    token = chaosiq_settings.get("token")
    return token


def get_service_url(settings: Settings) -> str:
    chaosiq_settings = settings.get("vendor", {}).get("chaosiq", {})
    url = chaosiq_settings.get("url")
    return url


def get_execution_id_from_extension(extensions: List[Extension] = None) -> str:
    if not extensions:
        return

    for extension in extensions:
        if extension["name"] == "chaosiq":
            return extension["execution_id"]


def set_execution_id_in_extension(execution_id: str, experiment: Experiment,
                                  extensions: List[Extension] = None) -> str:
    if extensions is None:
        extensions = experiment.setdefault("extensions", [])
        extensions.append({"name": "chaosiq"})

    for extension in extensions:
        if extension["name"] == "chaosiq":
            extension["execution_id"] = execution_id
            break
