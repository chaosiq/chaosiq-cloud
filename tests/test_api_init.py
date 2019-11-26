from copy import deepcopy

from chaoscloud.api import get_default_org, \
    get_chaosiq_extension_from_journal, get_execution_id, get_experiment_id, \
    set_execution_id


def test_get_default_org(organizations, default_org):
    assert get_default_org(organizations) == default_org


def test_get_no_orgs_when_no_default(default_org):
    other_org = deepcopy(default_org)
    other_org["default"] = False
    assert get_default_org([other_org]) is None


def test_get_journal_extensions():
    extension = {"name": "chaosiq"}
    extensions = [extension]

    journal = {
        "extensions": extensions
    }
    assert get_chaosiq_extension_from_journal(journal) == extension


def test_create_default_journal_extensions():
    journal = {}
    assert get_chaosiq_extension_from_journal(journal)["name"] == "chaosiq"


def test_get_execution_id_from_experiment_extensions():
    extension = {
        "name": "chaosiq",
        "execution_id": "1234"
    }
    extensions = [extension]
    assert get_execution_id(extensions) == "1234"


def test_get_no_execution_id_from_experiment_extensions_when_not_set():
    extension = {
        "name": "chaosiq"
    }
    extensions = [extension]
    assert get_execution_id(extensions) is None


def test_get_experiment_id_from_experiment_extensions():
    extension = {
        "name": "chaosiq",
        "experiment_id": "1234"
    }
    extensions = [extension]
    assert get_experiment_id(extensions) == "1234"


def test_get_no_experiment_id_from_experiment_extensions_when_not_set():
    extension = {
        "name": "chaosiq"
    }
    extensions = [extension]
    assert get_experiment_id(extensions) is None


def test_set_execution_id():
    extension = {
        "name": "chaosiq"
    }
    extensions = [extension]
    set_execution_id("1234", {"extensions": extensions})
    assert get_execution_id(extensions) == "1234"
