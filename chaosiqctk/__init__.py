# -*- coding: utf-8 -*-
from collections import namedtuple

from chaoslib.extension import get_extension
from chaoslib.types import Experiment, Settings

__version__ = '0.1.0'
__all__ = ["get_context"]


Context = namedtuple("Context", [
    "experiment",
    "token",
    "url"
])


def get_context(experiment: Experiment, source: str,
                settings: Settings) -> Context:
    """
    Load the current ChaosIQ context from the given parameters, in the
    following order (higher has more precedence):

    * as passed to the command line
    * from the "chaosiq" extension block (if any) in the experiment
    * from the settings under the chaosiq vendor section in the settings

    We may parse the URL from the source some day but for now, this sounds
    a little flaky.

    Additionaly, load the hub_url and token from the extension plugin
    settings.
    """
    token = url = None

    extension = get_extension(experiment, "chaosiq")
    if extension:
        pass

    if settings:
        plugin = settings.get('vendor', {}).get('chaosiq', {})
        url = plugin.get('url')
        token = plugin.get('token')

    context = Context(
        experiment=extension.get("experiment") if extension else None,
        url=url,
        token=token
    )

    return context
