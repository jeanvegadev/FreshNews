"""Useful functions."""
from resources.base import log
import time


def retry_decorator(retries=5, delay=5):
    """Decorator for retries."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            for attempt in range(1, retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    log.error(f"Attempt {attempt} failed: {e}")
                    if attempt == retries:
                        log.error(f"All {retries} attempts failed.")
                        raise
                    else:
                        log.info(f"Retrying in {delay} seconds...")
                        time.sleep(delay)
        return wrapper
    return decorator
