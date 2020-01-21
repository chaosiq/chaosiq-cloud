# -*- coding: utf-8 -*-
from chaoslib.caching import with_cache
from chaoslib.types import Experiment, Settings
from logzero import logger

__all__ = ["ensure_verification_is_valid", "run_verification"]


@with_cache
def ensure_verification_is_valid(verification: Experiment):
    logger.info("Verification looks valid")


@with_cache
def run_verification(verification: Experiment,
                     settings: Settings = None):
    logger.info("Running verification: {t}".format(t=verification["title"]))
