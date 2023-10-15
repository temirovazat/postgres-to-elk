import time
from functools import wraps
from typing import Any, Callable, Tuple

from core.logger import logger


def backoff(errors: Tuple, start_sleep_time=0.1, factor=2, border_sleep_time=10) -> Callable:
    """
    Retry a function after a certain period if an error occurs.

    Args:
        errors: Errors to be handled.
        start_sleep_time: Initial retry time.
        factor: How many times to increase the waiting time.
        border_sleep_time: Maximum waiting time.

    Returns:
        Callable: The decorated function.
    """
    def decorator(func) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = start_sleep_time
            while True:
                try:
                    conn = func(*args, **kwargs)
                except errors as message:
                    logger.error('Connection failed: {0}!'.format(message))
                    if delay < border_sleep_time:
                        delay *= 2
                    logger.error('Reconnecting in {0} seconds.'.format(delay))
                    time.sleep(delay)
                else:
                    return conn
        return wrapper
    return decorator
