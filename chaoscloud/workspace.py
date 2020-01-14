# -*- coding: utf-8 -*-
import copy
import io
import os
import yaml
from typing import Dict, Any, Optional, NoReturn

from logzero import logger

from chaoslib.types import Experiment
from .exceptions import WorkspaceException
from .types import Organization, Organizations, WorkspaceData
from .extension import get_extension_value

__all__ = ["initialize_workspace_path",
           "load_workspace", "save_workspace",
           "register_experiment_to_workspace",
           "get_experiment_metadata_from_workspace"]


WORKSPACE_FILENAME = ".chaosiq"

workspace_path = None
workspace_metadata = {}

# the workspace metadata dict contains the following structure:
# - experiments:
#   - <organization ID>:
#     - <experiment file name (with extension)>:
#       - <experiment ID>: <value>


def initialize_workspace_path(experiment_path: str):
    """
    Given an experiment path on the local file system,
    generates the related ChaosIQ workspace file, and
    keeps a reference to this internal file
    """
    set_workspace_path(
        os.path.join(os.path.dirname(experiment_path), WORKSPACE_FILENAME))


def set_workspace_path(path: str):
    """
    sets the path to the global variable
    """
    global workspace_path
    workspace_path = path


def get_workspace_path() -> str:
    """
    Returns the currently set workspace path
    """
    return workspace_path


def get_loaded_workspace_data() -> WorkspaceData:
    """
    Return the current workspace's data loaded from the hidden file
    on the file system alongside the experiment
    """
    return copy.deepcopy(workspace_metadata)


def set_workspace_data(data: WorkspaceData) -> NoReturn:
    """
    Sets new data as the global available workspace
    """
    global workspace_metadata
    workspace_metadata = data


def reset_workspace() -> NoReturn:
    set_workspace_data({})


def load_workspace(path: str = None) -> NoReturn:
    """
    Parse the given workspace's internal files from `path` and load them.
    """
    path = path or workspace_path

    if not os.path.exists(path):
        logger.debug(
            "The ChaosIQ workspace file could not be found at "
            "'{}'.".format(path))
        return

    with io.open(path) as f:
        try:
            set_workspace_data(yaml.safe_load(f))
        except yaml.YAMLError as ye:
            raise WorkspaceException(
                "Failed parsing workspace YAML file {}: {}".format(
                    path, str(ye)))


def save_workspace(path: str = None) -> NoReturn:
    """
    Save the experiments context into the internal workspace file
    on the local file system
    """
    path = path or workspace_path
    if path is None:
        return

    logger.debug("Saving workspace at {}".format(path))
    try:
        with io.open(path, 'w') as outfile:
            yaml.dump(workspace_metadata, outfile, default_flow_style=False)
    except (yaml.YAMLError, OSError, IOError) as error:
        raise WorkspaceException(
            "Failed saving workspace YAML file to {}: {}".format(
                path, str(error)))


def register_experiment_to_workspace(
        experiment: Experiment,
        organizations: Organizations,
        experiment_path: str = None) -> NoReturn:
    """
    Register the link between the experiment ID and the experiment path
    into the workspace related to the experiment's location
    on the local file system.

    This link experiment path -> experiment ID allows to associate
    several executions with the same experiment on the console.
    The link is registered for the current/active organization ID.
    """
    if experiment_path is None:
        experiment_path = get_experiment_path(experiment)

    if not experiment_path:
        return

    if not os.path.exists(experiment_path):
        return

    experiment_id = get_experiment_id(experiment)
    experiment_name = os.path.basename(experiment_path)
    org = get_default_org(organizations)
    organization_id = org["id"]
    team = get_default_team(org)
    team_id = team["id"]

    logger.debug(
        "Registering experiment '{name}' with ID '{id}' "
        "for organization '{org}' and team '{team}'".format(
            name=experiment_name, id=experiment_id,
            org=organization_id, team=team_id))

    meta = workspace_metadata.\
        setdefault("experiments", {}).\
        setdefault(organization_id, {}). \
        setdefault(team_id, {}). \
        setdefault(experiment_name, {})
    meta["experiment_id"] = experiment_id


def get_experiment_metadata_from_workspace(
        experiment: Experiment,
        organizations: Organizations,
        experiment_path: str = None) -> Optional[Dict[str, Any]]:
    """
    For the loaded workspace, check whether the experiment ID exists
    for the experiment path related to the given organization

    If the experiment path is not recognized in the workspace,
    this is returning None as response ie unknown experiment
    (probably a new experiment file, or maybe path has changed)
    """
    if experiment_path is None:
        experiment_path = get_experiment_path(experiment)

    if not experiment_path:
        return

    organization_id = get_default_org_id(organizations)
    team_id = get_default_team_id(get_default_org(organizations))
    experiment_name = os.path.basename(experiment_path)
    return workspace_metadata.\
        get("experiments", {}).\
        get(organization_id, {}). \
        get(team_id, {}). \
        get(experiment_name, {})


###############################################################################
# Internals
###############################################################################
def get_experiment_path(experiment: Experiment) -> Optional[str]:
    return get_extension_value(experiment, "experiment_path")


def get_experiment_source(experiment: Experiment) -> Optional[str]:
    return get_extension_value(experiment, "source")


def get_experiment_id(experiment: Experiment) -> str:
    return get_extension_value(experiment, "experiment_id")


def get_default_org(organizations: Organizations) -> Organization:
    for org in organizations:
        if org.get('default') is True:
            return org


def get_default_org_id(organizations: Organizations) -> Optional[str]:
    org = get_default_org(organizations)
    if org:
        return org["id"]


def get_default_team(org: Dict[str, str]) -> Optional[Dict[str, Any]]:
    teams = org.get('teams', [])
    for team in teams:
        if team['default']:
            return team


def get_default_team_id(org: Organization) -> Optional[str]:
    team = get_default_team(org)
    if team:
        return team["id"]
