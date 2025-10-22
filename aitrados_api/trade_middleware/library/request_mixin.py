import enum
import json
import asyncio
import threading
import uuid
import time
from abc import ABC
from typing import Callable, Any
import zmq
import zmq.asyncio
from loguru import logger

from aitrados_api.trade_middleware.client_adresss_detector import FrontendAddressDetector


class AsyncFrontendRequestMixin:
    """Frontend request client - static method implementation"""

    @classmethod
    def _generate_request_id(cls) -> str:
        """Generate simple request ID"""
        return f"req-{int(time.time() * 1000)}-{uuid.uuid4().hex[:6]}"

    @classmethod
    def _serialize_params(cls, *args, **kwargs) -> bytes:
        """Serialize parameters"""
        data = {
            "args": args,
            "kwargs": kwargs
        }
        return json.dumps(data).encode('utf-8')

    @classmethod
    def _deserialize_response(cls, response: bytes) -> Any:
        """Deserialize response"""
        try:
            return json.loads(response.decode('utf-8'))
        except:
            return response.decode('utf-8')

    @classmethod
    async def _create_temp_socket_async(cls, timeout: float = 10.0):
        """Create temporary async socket"""
        ctx = zmq.asyncio.Context()
        socket = ctx.socket(zmq.REQ)

        # Set timeout (milliseconds)
        socket.setsockopt(zmq.RCVTIMEO, int(timeout * 1000))
        socket.setsockopt(zmq.SNDTIMEO, int(timeout * 1000))

        # Set temporary identity
        identity = f"temp-{cls._generate_request_id()}".encode()
        socket.setsockopt(zmq.IDENTITY, identity)

        addr = FrontendAddressDetector.get_cached_type()

        socket.connect(addr)

        return ctx, socket

    @classmethod
    def _create_temp_socket_sync(cls, timeout: float = 10.0):
        """Create temporary sync socket"""
        ctx = zmq.Context()
        socket = ctx.socket(zmq.REQ)

        # Set timeout (milliseconds)
        socket.setsockopt(zmq.RCVTIMEO, int(timeout * 1000))
        socket.setsockopt(zmq.SNDTIMEO, int(timeout * 1000))

        # Set temporary identity
        identity = f"temp-{cls._generate_request_id()}".encode()
        socket.setsockopt(zmq.IDENTITY, identity)

        addr = FrontendAddressDetector.get_cached_type()
        socket.connect(addr)

        return ctx, socket

    @classmethod
    async def call_sync(cls, backend_identity: str, function_name: str | enum.Enum,
                        *args, timeout: float = 10.0, **kwargs) -> Any:
        """Synchronous call (block and wait for result)"""
        ctx, socket = await cls._create_temp_socket_async(timeout)

        if isinstance(function_name, enum.Enum):
            function_name = function_name.value

        try:
            # Serialize parameters
            params = cls._serialize_params(*args, **kwargs)

            # Send request: [empty, backend_identity, function_name, params]
            await socket.send_multipart([
                backend_identity.encode(),
                function_name.encode(),
                params
            ])

            # logger.debug(f"[Client] Send sync request: {backend_identity}.{function_name}")

            # Wait for response
            try:
                response_parts = await socket.recv_multipart()

                if len(response_parts) >= 3:
                    recv_backend, recv_function, response = response_parts[:3]

                    if recv_backend == b"ERROR":
                        raise Exception(f"Backend error: {response.decode()}")

                    result = cls._deserialize_response(response)

                    return result
                else:
                    raise Exception("Response format error")

            except zmq.Again:
                error_advisor = """
Reasons: 
1.Please make sure to run the trade middleware instance before making requests.
from aitrados_api.universal_interface.trade_middleware_instance import AitradosTradeMiddlewareInstance
AitradosTradeMiddlewareInstance.run_all()
2.host address is correct?
3.network is slow or blocked? set timeout more bigger number
                """

                raise TimeoutError(f"Timeout ({timeout}s).{error_advisor}")

        except Exception as e:
            logger.error(f"[Client] call_sync failed: {e}")
            raise
        finally:
            socket.close()
            ctx.term()

    @classmethod
    def call_async(cls, backend_identity: str, function_name: str | enum.Enum,
                   callback: Callable, *args, timeout: float = 10.0, **kwargs):
        """Async call (handle result with callback)"""
        if isinstance(function_name, enum.Enum):
            function_name = function_name.value

        def _thread_worker():
            """Execute async call in independent thread"""
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            async def _async_call():
                try:
                    result = await cls.call_sync(backend_identity, function_name,
                                                 *args, timeout=timeout, **kwargs)
                    callback(result, error=None)
                except Exception as e:
                    callback(None, error=e)

            try:
                loop.run_until_complete(_async_call())
            finally:
                loop.close()

        # Execute in new thread
        thread = threading.Thread(target=_thread_worker, daemon=True)
        thread.start()
        return thread

    @classmethod
    def call_fire_and_forget(cls, backend_identity: str, function_name: str | enum.Enum,
                             *args, **kwargs):

        """Fire and forget call (send without caring about result)"""
        if isinstance(function_name, enum.Enum):
            function_name = function_name.value

        def _thread_worker():
            """Execute send in independent thread"""
            ctx, socket = cls._create_temp_socket_sync(timeout=5.0)  # Short timeout

            try:
                params = cls._serialize_params(*args, **kwargs)

                # Send request
                socket.send_multipart([
                    backend_identity.encode(),
                    function_name.encode(),
                    params
                ])

                logger.debug(f"[Client] Send fire-and-forget request: {backend_identity}.{function_name}")

                # Return immediately, don't wait for response (but socket will still receive response)
                # Here we can choose to receive and discard response, or close directly

                try:
                    socket.recv_multipart(zmq.NOBLOCK)  # Non-blocking receive and discard
                except zmq.Again:
                    pass  # Ignore if no response
                return True

            except Exception as e:
                logger.warning(f"[Client] Fire-and-forget request failed: {e}")
            finally:
                # Clean up resources
                socket.close()
                ctx.term()
            return False

        return _thread_worker()




# Convenient wrapper for sync version
class FrontendRequestMixin:
    """Sync frontend request client - convenient wrapper"""

    @classmethod
    def call_sync(cls, backend_identity: str, function_name: str | enum.Enum,
                  *args, timeout: float = 10.0, **kwargs) -> Any:
        """Synchronous call"""
        # Run async method in new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            return loop.run_until_complete(
                AsyncFrontendRequestMixin.call_sync(backend_identity, function_name,
                                               *args, timeout=timeout, **kwargs)
            )
        finally:
            loop.close()

    @classmethod
    def call_async(cls, backend_identity: str, function_name: str | enum.Enum,
                   callback: Callable, *args, timeout: float = 10.0, **kwargs):
        """Async call (with callback)"""
        return AsyncFrontendRequestMixin.call_async(backend_identity, function_name,
                                               callback, *args, timeout=timeout, **kwargs)

    @classmethod
    def call_fire_and_forget(cls, backend_identity: str, function_name: str | enum.Enum,
                             *args, **kwargs):
        """Fire and forget call"""
        return AsyncFrontendRequestMixin.call_fire_and_forget(backend_identity, function_name,
                                                         *args, **kwargs)