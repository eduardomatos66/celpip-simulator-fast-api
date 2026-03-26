import time
import functools
import asyncio
import logging
from typing import Any, Callable

logger = logging.getLogger(__name__)

def log_execution_time(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to log the execution time of a function."""
    
    @functools.wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            return await func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            logger.info(
                f"Service method {func.__module__}.{func.__name__} executed in {duration:.4f}s"
            )

    @functools.wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            end_time = time.perf_counter()
            duration = end_time - start_time
            logger.info(
                f"Service method {func.__module__}.{func.__name__} executed in {duration:.4f}s"
            )

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
