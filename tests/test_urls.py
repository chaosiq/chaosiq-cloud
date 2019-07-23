# -*- coding: utf-8 -*-
import uuid

from chaoscloud.api import urls

ENDPOINT = "https://chaostoolkit.com"


def test_build_base_url():
    assert urls.base(ENDPOINT) == "{}/api/v1".format(ENDPOINT)


def test_build_experiments_url():
    base = urls.base(ENDPOINT)
    assert urls.experiment(base) == \
        "{}/api/v1/experiments".format(ENDPOINT)


def test_build_experiment_url():
    base = urls.base(ENDPOINT)
    experiment_id = str(uuid.uuid4())
    assert urls.experiment(base, experiment_id) == \
        "{}/api/v1/experiments/{}".format(ENDPOINT, experiment_id)


def test_build_executions_url():
    base = urls.base(ENDPOINT)
    assert urls.execution(base) == "{}/api/v1/executions".format(ENDPOINT)


def test_build_policies_url():
    base = urls.base(ENDPOINT)
    assert urls.policy(base) == "{}/api/v1/policies".format(ENDPOINT)


def test_clean_url_when_api_not_in_path():
    assert urls.clean(ENDPOINT) == ENDPOINT


def test_clean_url_when_api_is_in_path():
    base = "{}/api/experiments".format(ENDPOINT)
    assert urls.clean(base) == "{}/experiments".format(ENDPOINT)


def test_get_host():
    assert urls.host(ENDPOINT) == "chaostoolkit.com"


def test_get_host_with_port():
    assert urls.host("http://localhost:8989/whatever") == "localhost:8989"
