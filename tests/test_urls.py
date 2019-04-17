# -*- coding: utf-8 -*-
import uuid

from chaoscloud.api import urls

ENDPOINT = "https://chaostoolkit.com"


def test_build_base_url():
    assert urls.base(ENDPOINT) == f"{ENDPOINT}/api/v1"


def test_build_experiments_url():
    base = urls.base(ENDPOINT)
    assert urls.experiment(base) == f"{ENDPOINT}/api/v1/experiments"


def test_build_experiment_url():
    base = urls.base(ENDPOINT)
    experiment_id = str(uuid.uuid4())
    assert urls.experiment(base, experiment_id) == \
        f"{ENDPOINT}/api/v1/experiments/{experiment_id}"


def test_build_executions_url():
    base = urls.base(ENDPOINT)
    assert urls.execution(base) == f"{ENDPOINT}/api/v1/executions"


def test_build_policies_url():
    base = urls.base(ENDPOINT)
    assert urls.policy(base) == f"{ENDPOINT}/api/v1/policies"


def test_clean_url_when_api_not_in_path():
    assert urls.clean(ENDPOINT) == ENDPOINT


def test_clean_url_when_api_is_in_path():
    base = f"{ENDPOINT}/api/experiments"
    assert urls.clean(base) == f"{ENDPOINT}/experiments"


def test_get_host():
    assert urls.host(ENDPOINT) == "chaostoolkit.com"


def test_get_host_with_port():
    assert urls.host("http://localhost:8989/whatever") == "localhost:8989"
