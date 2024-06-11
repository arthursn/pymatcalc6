import os
import sys
import warnings
from contextlib import contextmanager

__all__ = ["suppressing_stdout"]

STDOUT_FILENO = -1
STDOUT_DUPLICATE = -1
try:
    STDOUT_FILENO = sys.stdout.fileno()
    STDOUT_DUPLICATE = os.dup(STDOUT_FILENO)
except Exception:
    pass


@contextmanager
def suppressing_stdout():
    """
    Suppress stdout in context
    """
    if STDOUT_FILENO < 0:
        warnings.warn("stdout suppression not available in this environment")
        return

    os.close(STDOUT_FILENO)
    os.dup2(os.open(os.devnull, os.O_WRONLY), STDOUT_FILENO)

    try:
        yield
    finally:
        os.close(STDOUT_FILENO)
        os.dup2(STDOUT_DUPLICATE, STDOUT_FILENO)
