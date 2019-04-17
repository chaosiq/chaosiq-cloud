from typing import Dict, List
import uuid

import pytest


@pytest.fixture
def default_org_id() -> str:
    return str(uuid.uuid4())


@pytest.fixture
def default_org(default_org_id: str) -> Dict[str, str]:
    return {
        "id": default_org_id,
        "name": "myorg",
        "default": True
    }


@pytest.fixture
def organizations(default_org: Dict[str, str]) -> List[Dict[str, str]]:
    return [default_org]
