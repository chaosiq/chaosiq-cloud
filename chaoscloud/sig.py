import signal
import threading
from typing import Any, NoReturn

from chaoslib.exceptions import InterruptExecution
from logzero import logger

__all__ = ["register_cleanup_on_forced_exit"]


def register_cleanup_on_forced_exit() -> NoReturn:
    """
    Try to ensure a clean exit on certain signals such as SIGTERM.
    """
    if threading.current_thread() is threading.main_thread():
        signal.signal(signal.SIGTERM, interrupt_execution)


###############################################################################
# Internals
###############################################################################
def interrupt_execution(signum: int, frame: Any) -> NoReturn:
    """
    Raises `InterruptExecution` so that the experiment terminates gracefully.
    """
    msg = "Caught signal {}. Interrupting the execution...".format(signum)
    logger.debug(msg)
    raise InterruptExecution(msg)
