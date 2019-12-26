from typing import Any, Dict, List
import uuid

import pytest


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
