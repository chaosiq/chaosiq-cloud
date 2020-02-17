# -*- coding: utf-8 -*-

from chaoslib.exceptions import ChaosException


__all__ = ["WorkspaceException", "MissingVerificationIdentifier"]


class WorkspaceException(ChaosException):
    pass


class MissingVerificationIdentifier(ChaosException):
    pass
