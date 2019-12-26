# -*- coding: utf-8 -*-
import os
from tempfile import NamedTemporaryFile
from unittest.mock import patch

from chaoscloud.workspace import workspace_metadata, \
    set_workspace_path, get_workspace_path, initialize_workspace_path, \
    get_loaded_workspace_data, set_workspace_data, reset_workspace, \
    load_workspace, save_workspace, register_experiment_to_workspace, \
    get_experiment_metadata_from_workspace
from chaoscloud.exceptions import WorkspaceException


EMPTY_VALUES = (None, '', [], (), {})


def test_set_custom_workspace_path():
    assert get_workspace_path() is None

    tests_folder = os.path.dirname(__name__)

    p = os.path.join(tests_folder, '.dummy')
    set_workspace_path(p)
    assert get_workspace_path() == p

    # reset workspace path at end of test
    set_workspace_path(None)


def test_initialize_experiments_workspace_path():
    assert get_workspace_path() is None

    tests_folder = os.path.dirname(__name__)

    exp_path = os.path.join(tests_folder, 'dummy-experiment.json')
    ws_path = os.path.join(tests_folder, ".chaosiq")

    initialize_workspace_path(exp_path)
    assert get_workspace_path() == ws_path

    # reset workspace path at end of test
    set_workspace_path(None)


def test_set_workspace_data():
    data = {"dummy": "data"}
    set_workspace_data(data)
    assert get_loaded_workspace_data() == data

    # clean up
    reset_workspace()


def test_reset_workspace_data():
    set_workspace_data({"dummy": "data"})
    assert get_loaded_workspace_data() not in EMPTY_VALUES

    reset_workspace()
    assert get_loaded_workspace_data() in EMPTY_VALUES


def test_get_loaded_workspace_data_cannot_be_mutated():
    set_workspace_data({"dummy": "data"})

    data1 = get_loaded_workspace_data()
    data2 = get_loaded_workspace_data()
    assert data1 == data2

    # mutate one of the data dict and check the other one is not
    # neither the global workspace variable
    data1["extra"] = "value"
    assert data1 != data2
    assert data1 != workspace_metadata
    assert data1 != get_loaded_workspace_data()
    assert data2 == get_loaded_workspace_data()

    # clean up
    reset_workspace()


def test_load_workspace_invalid_path():
    load_workspace('/tmp/invalid')
    assert get_loaded_workspace_data() in EMPTY_VALUES


def test_load_workspace_invalid_yaml():
    with NamedTemporaryFile(suffix="yaml", mode="w") as workspace:
        workspace.write('- "invalid" "yaml"')
        workspace.seek(0)

        try:
            load_workspace(workspace.name)
        except WorkspaceException:
            assert True, "WorkspaceException has been raised."
        else:
            assert False, "WorkspaceException has NOT been raised."


def test_load_workspace():
    with NamedTemporaryFile(suffix="yaml", mode='w') as workspace:
        workspace.write("experiments:\n")
        workspace.write("  chaosiq:\n")
        workspace.write("    test:\n")
        workspace.write("      dummy.json:\n")
        workspace.write("        experiment_id: azerty123456\n")
        workspace.seek(0)

        load_workspace(workspace.name)
        data = get_loaded_workspace_data()
        assert data == {
            "experiments": {
                "chaosiq": {
                    "test": {
                        "dummy.json": {
                            "experiment_id": "azerty123456"
                        }
                    }
                }
            }
        }

    # clean up
    reset_workspace()


def test_save_workspace():
    set_workspace_data({"experiments": {}})

    with NamedTemporaryFile(suffix="yaml", mode='w') as workspace:
        save_workspace(workspace.name)

    # clean up
    reset_workspace()


def test_save_workspace_non_writable_file():
    with NamedTemporaryFile(suffix="yaml") as workspace:
        os.chmod(workspace.name, 0o500)

        try:
            save_workspace(workspace.name)
        except WorkspaceException:
            assert True, "WorkspaceException has been raised."
        else:
            assert False, "WorkspaceException has NOT been raised."


def test_register_experiment_without_path():
    experiment = {
        "title": "hello"
    }
    register_experiment_to_workspace(experiment, [])
    assert get_loaded_workspace_data() == {}


def test_register_experiment_path_does_not_exist():
    experiment = {
        "title": "hello"
    }
    register_experiment_to_workspace(experiment, [], '/tmp/experiment.json')
    assert get_loaded_workspace_data() == {}


@patch("os.path.exists")
def test_register_experiment(mock_exists, organizations,
                             default_org_id, default_team_id):
    mock_exists.return_value = True

    experiment = {
        "title": "hello",
        "extensions": [
            {
                "name": "chaosiq",
                "experiment_id": "azerty123456",
                "experiment_path": "/tmp/experiment.json"
            }
        ]
    }

    register_experiment_to_workspace(experiment, organizations)
    assert get_loaded_workspace_data() != {}
    data = get_loaded_workspace_data()
    assert "experiment.json" in \
           data["experiments"][default_org_id][default_team_id]

    # clean up
    reset_workspace()


@patch("os.path.exists")
def test_fetch_experiment_metadata(mock_exists, organizations,
                                   default_org_id, default_team_id):
    mock_exists.return_value = True

    set_workspace_data({
        "experiments": {
            default_org_id: {
                default_team_id: {
                    "experiment.json": {
                        "experiment_id": "azerty123456"
                    }
                }
            }
        }
    })

    experiment = {
        "title": "hello"
    }
    experiment_meta = get_experiment_metadata_from_workspace(
        experiment, organizations, experiment_path="/tmp/experiment.json")
    assert experiment_meta["experiment_id"] == "azerty123456"

    # clean up
    reset_workspace()
