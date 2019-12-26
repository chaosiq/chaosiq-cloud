# -*- coding: utf-8 -*-
from typing import Any, List
from contextlib import contextmanager

from chaoslib.types import Experiment

__all__ = ["get_extension_value", "set_extension_value",
           "del_extension_value", "remove_sensitive_extension_values"]


def get_extension_value(experiment: Experiment,
                        key: str, default: Any = None):
    extensions = experiment.setdefault("extensions", [])
    for extension in extensions:
        ext_name = extension.get("name")
        if ext_name == "chaosiq":
            return extension.get(key, default)


def set_extension_value(experiment: Experiment, key: str, value: Any):
    extensions = experiment.setdefault("extensions", [])
    for extension in extensions:
        ext_name = extension.get("name")
        if ext_name == "chaosiq":
            extension[key] = str(value)
            break
    else:
        extensions.append({
            "name": "chaosiq",
            key: value
        })


def del_extension_value(experiment: Experiment, key: str, silent: bool = True):
    extensions = experiment.setdefault("extensions", [])
    for extension in extensions:
        ext_name = extension.get("name")
        if ext_name == "chaosiq":
            try:
                del extension[key]
            except KeyError:
                if not silent:
                    raise


class SensitiveManager:
    """
    This class provides utility functions to remove & restore
    sensitive values from the experiment extension
    """
    def __init__(self):
        self.sensitive = {}

    def remove_sensitive_values(self, experiment: Experiment,
                                keys: List[str] = None):
        if keys is None:
            return

        for key in keys:
            self.sensitive[key] = get_extension_value(experiment, key)
            del_extension_value(experiment, key, silent=True)

    def restore_sensitive_values(self, experiment: Experiment,
                                 keys: List[str] = None):
        if keys is None:
            return

        for key in keys:
            set_extension_value(experiment, key, self.sensitive[key])


@contextmanager
def remove_sensitive_extension_values(experiment: Experiment,
                                      keys: List[str] = None):
    """
    context manager for a block that needs to have experiment available
    without sensitive data.

    it removes the sensitive when entering the with block, then
    restores them when leaving it.
    """
    try:
        sm = SensitiveManager()
        sm.remove_sensitive_values(experiment, keys)
        yield
    finally:
        sm.restore_sensitive_values(experiment, keys)
