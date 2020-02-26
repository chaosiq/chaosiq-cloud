import tempfile
import uuid
from typing import Any, Dict, List

import pytest

from chaoscloud.api import urls

ENDPOINT = "https://chaosiq.io"


@pytest.fixture
def default_org_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def default_team_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def default_team(default_team_id: str) -> str:
    return {
        "id": default_team_id,
        "name": "myteam",
        "default": True
    }


@pytest.fixture
def default_org(default_org_id: str,
                default_team: Dict[str, Any]) -> Dict[str, str]:
    return {
        "id": default_org_id,
        "name": "myorg",
        "default": True,
        "teams": [default_team]
    }


@pytest.fixture
def organizations(default_org: Dict[str, str]) -> List[Dict[str, str]]:
    return [default_org]


@pytest.fixture
def settings() -> Dict[str, Any]:
    return {
        "controls":
            {
                "chaosiq-cloud": {
                    "features": {
                        "publish": 'on',
                        "safeguards": 'on',
                        "workspace": 'on'
                    }
                }
            }
    }


@pytest.fixture(scope='function')
def log_file():
    with tempfile.NamedTemporaryFile() as f:
        yield f


@pytest.fixture
def base_team_url(default_org_id: str, default_team_id: str) -> str:
    return urls.full(
        urls.base(ENDPOINT), default_org_id, default_team_id)


@pytest.fixture
def default_settings(default_org_id: str,
                     default_team_id: str) -> Dict[str, Any]:
    return {
        "controls": {
            "chaosiq-cloud": {
                "features": {
                    "publish": 'on',
                    "safeguards": 'on',
                    "workspace": 'on'
                },
                "provider": {
                    "arguments": {
                        "url": ENDPOINT,
                        "organizations": [
                           {
                                "default": True,
                                "id": default_org_id,
                                "name": "Super Org",
                                "teams": [
                                    {
                                        "default": True,
                                        "id": default_team_id,
                                        "name": "Super Team"
                                    }
                                ]
                           }
                        ]
                    }
                }
            }
        }
    }
