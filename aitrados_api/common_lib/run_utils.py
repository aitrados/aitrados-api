
import asyncio
import concurrent
import threading
from typing import Awaitable, Any


def _asyncio_run_in_background(coro, daemon=True):
    def _runner():
        asyncio.run(coro)

    t = threading.Thread(target=_runner, daemon=daemon)
    t.start()


def run_async_function_without_block(func):
    # Run async function in sync function without blocking
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:  # 'RuntimeError: There is no current event loop...'
        loop = None

    if loop and loop.is_running():

        loop.create_task(func)
    else:
        _asyncio_run_in_background(func)


def run_async_function_with_block(coro: Awaitable[Any]) -> Any:
    # Blocking call to a coroutine, automatically handle whether there's already a running event loop and close temporary loop
    if not asyncio.iscoroutine(coro) and not isinstance(coro, asyncio.Future):
        raise TypeError("coro must be a coroutine or Future")

    try:
        running_loop = asyncio.get_running_loop()
    except RuntimeError:
        running_loop = None

    if running_loop and running_loop.is_running():
        # Current thread already has running loop: create and run new loop in separate thread
        def _runner():
            loop = asyncio.new_event_loop()
            try:
                asyncio.set_event_loop(loop)
                return loop.run_until_complete(coro)
            finally:
                loop.close()

        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
            return ex.submit(_runner).result()
    else:
        # No running loop: directly use asyncio.run (will automatically create and close loop)
        return asyncio.run(coro)


async def run_sync_function_without_block_asynchronous(fun, *args, **kwargs):
    # Run sync function in async function without blocking async loop
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, lambda: fun(*args, **kwargs))


class ExecuteCallback:

    @classmethod
    async def arun(cls, callback, *args, **kwargs):
        if not callback:
            return None
        if asyncio.iscoroutinefunction(callback):
            return await callback(*args, **kwargs)
        else:
            return callback(*args, **kwargs)

    @classmethod
    async def arun_background(cls, callback, *args, **kwargs):
        """Execute callback (sync or async) in background non-blocking, don't wait for completion"""
        if not callback:
            return None

        if asyncio.iscoroutinefunction(callback):
            asyncio.create_task(callback(*args, **kwargs))
        else:
            loop = asyncio.get_running_loop()
            loop.run_in_executor(None, lambda: callback(*args, **kwargs))

    @classmethod
    def run(cls, callback, *args, **kwargs):
        """Synchronously execute callback (sync or async), block and wait for completion and return result"""
        if not callback:
            return None
        if asyncio.iscoroutinefunction(callback):
            return run_async_function_with_block(callback(*args, **kwargs))
        else:
            return callback(*args, **kwargs)

    @classmethod
    def run_background(cls, callback, *args, **kwargs):
        """Execute callback (sync or async) in background thread non-blocking, don't wait for completion"""
        if not callback:
            return None

        def _execute():
            if asyncio.iscoroutinefunction(callback):
                # Async callback: create loop in new thread and run
                loop = asyncio.new_event_loop()
                try:
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(callback(*args, **kwargs))
                finally:
                    loop.close()
            else:
                # Sync callback: call directly
                callback(*args, **kwargs)

        import threading
        thread = threading.Thread(target=_execute, daemon=True)
        thread.start()