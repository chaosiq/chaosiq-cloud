# -*- coding: utf-8 -*-
from chaoslib.exceptions import ChaosException

__all__ = ["VerificationException", "InvalidVerification"]


class VerificationException(ChaosException):
    pass


class InvalidVerification(VerificationException):
    pass
