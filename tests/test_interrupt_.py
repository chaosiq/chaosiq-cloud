import os
import signal
import threading
import time

from chaoslib.exceptions import InterruptExecution
import pytest

from chaoscloud.sig import register_cleanup_on_forced_exit


def test_raises_interrupt_on_sigterm():
    register_cleanup_on_forced_exit()

    pid = os.getpid()

    def send_sigterm():
        time.sleep(1)
        os.kill(pid, signal.SIGTERM)

    thread = threading.Thread(target=send_sigterm)
    thread.daemon = True
    thread.start()

    with pytest.raises(InterruptExecution):
        time.sleep(2)
