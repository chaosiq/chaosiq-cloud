# -*- coding: utf-8 -*-
from contextlib import contextmanager
from typing import Any, Dict, Generator, List

from chaoslib.types import Settings
from logzero import logger
from requests import Session

from . import urls

__all__ = ["client_session"]


@contextmanager
def client_session(url: str, organizations: List[Dict[str, str]],
                   verify_tls: bool = True, settings: Settings = None) \
                       -> Generator[Session, None, None]:
    """
    Creates a HTTP session that injects authorization header into each
    request made with this session.
    """
    org = get_default_org(organizations)
    org_id = org["id"]
    host = urls.host(url)
    headers = {
        "Accept": "application/json",
    }

    # read the token from the auths block
    settings = settings or {}
    auths = settings.get('auths')
    if auths:
        host_auth = auths.get(host)
        if not host_auth:
            logger.debug(
                "Your settings are missing an authentication declaration for "
                "'{}'. Have you run 'chaos login'?".format(host))
        else:
            auth_type = host_auth.get('type', 'bearer')
            token = host_auth.get('value')
            headers["Authorization"] = "{} {}".format(
                auth_type.capitalize(), token)

    with Session() as s:
        s.base_url = urls.org(urls.base(url), organization_id=org_id)
        s.headers.update(headers)
        s.verify = verify_tls
        yield s


def get_default_org(organizations: List[Dict[str, str]]) -> Dict[str, Any]:
    for org in organizations:
        if org.get('default') is True:
            return org
