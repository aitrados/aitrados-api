import asyncio
import os
import time
from threading import RLock

import zmq
import zmq.asyncio
from aitrados_api.common_lib.common import run_asynchronous_function, is_debug
from aitrados_api.common_lib.response_format import ErrorResponse, UnifiedResponse
from loguru import logger
from typing import Dict

from aitrados_api.trade_middleware.client_adresss_detector import CommAddressDetector, IntelligentRouterContext
from aitrados_api.trade_middleware.intelligent_router_address import FrontendIntelligentRouterAddress, \
    BackendIntelligentRouterAddress, cleanup_sockets


class AsyncRPCIntelligentRouter:

    HEARTBEAT_INTERVAL = 5       # Backend heartbeat interval
    HEARTBEAT_TIMEOUT = 15       # If there is no heartbeat for a certain period of time, it is considered as disconnected.

    def __init__(self):
        self.ctx = zmq.asyncio.Context.instance()
        IntelligentRouterContext.async_rpc=self.ctx
        self.frontend = self.ctx.socket(zmq.ROUTER)
        self.backend = self.ctx.socket(zmq.ROUTER)
        self.tag_to_identity: Dict[str, bytes] = {}
        self.last_seen: Dict[str, float] = {}
        self._stop = False
        self._lock=RLock()

    async def bind(self):
        for addr in FrontendIntelligentRouterAddress.get_array():
            try:
                self.frontend.bind(addr)
                #logger.info(f"[RPC Frontend] Binding successful: {addr}")
            except Exception as e:
                logger.error(f"[RPC Frontend] Binding failed {addr}: {e}")
                exit()

        for addr in BackendIntelligentRouterAddress.get_array():
            try:
                self.backend.bind(addr)
                #logger.info(f"[RPC Backend] Binding successful: {addr}")
            except Exception as e:
                logger.error(f"[RPC Backend] Binding failed {addr}: {e}")
                exit()

        CommAddressDetector.save_machine_id()
        os.environ["TRADE_MIDDLEWARE_PID"]=str(os.getpid())
    async def start(self):
        poller = zmq.asyncio.Poller()
        poller.register(self.frontend, zmq.POLLIN)
        poller.register(self.backend, zmq.POLLIN)

        asyncio.create_task(self._heartbeat_monitor())

        logger.info("🌐 RPC Router Started")
        if is_debug():
            logger.debug(f"                         RPC frontend addr:{FrontendIntelligentRouterAddress.get_array()}")
            logger.debug(f"                         RPC backend addr:{BackendIntelligentRouterAddress.get_array()}")

        while not self._stop:
            events = dict(await poller.poll(timeout=1000))

            # Receive front-end requests
            if self.frontend in events:
                await self._handle_frontend_request()

            # Receive backend registration or reply
            if self.backend in events:
                await self._handle_backend_message()


    def get_all_online_backend_services(self):
        backend_identities=[]
        if self.tag_to_identity:
            backend_identities =list(self.tag_to_identity.keys())
        return UnifiedResponse(result=backend_identities).model_dump_json()



    async def _handle_frontend_request(self):
        msg = await self.frontend.recv_multipart()
        if len(msg) < 5:
            logger.warning(f"[RPC Frontend] Request format error: {msg}")
            return

        client_id, empty, backend_identity, function_name, params = msg[:5]
        if function_name==b"get_all_online_backend_services":
            data=self.get_all_online_backend_services()
            await self.frontend.send_multipart([client_id, b"", backend_identity, function_name, data.encode()])


        backend_identity_str = backend_identity.decode()


        target_id = self.tag_to_identity.get(backend_identity_str)

        if not target_id:
            logger.warning(f"[RPC Router] Backend not found: {backend_identity}")
            message=f"backend_identity {backend_identity_str} not found,Available backend_identities in {list(self.tag_to_identity.keys())}"
            data=ErrorResponse(code=429,message=message).model_dump_json()
            await self.frontend.send_multipart([client_id, b"", backend_identity, function_name,data.encode()])
            return

        # Pass the request to the backend
        await self.backend.send_multipart([
            target_id,
            b"",
            client_id,
            backend_identity,
            function_name,
            params
        ])

    async def _handle_backend_message(self):

        msg = await self.backend.recv_multipart()

        if len(msg) < 2:
            return

        backend_id = msg[0]
        empty = msg[1]
        parts = msg[2:]

        if not parts:
            return

        cmd = parts[0].decode()

        # 1️⃣ register
        if cmd == "REGISTER" and len(parts) >= 2:
            with self._lock:
                backend_identity = parts[1].decode()
                self.tag_to_identity[backend_identity] = backend_id
                self.last_seen[backend_identity] = time.time()
                #logger.info(f"[Router] Registered the backend: {backend_identity} -> {backend_id}")
                logger.info(f"🤝[RPC Router] Registered Well: {backend_identity}")

        # 2️⃣ heartbeat
        elif cmd == "HEARTBEAT" and len(parts) >= 2:
            backend_identity = parts[1].decode()
            #print("HEARTBEAT", backend_identity,self.tag_to_identity)
            with self._lock:
                self.last_seen[backend_identity] = time.time()
                if backend_identity not in self.tag_to_identity:
                    self.tag_to_identity[backend_identity] = backend_id

        # 3️⃣ Business Response
        else:
            # format: [backend_id, '', client_id, backend_identity, function_name, response]
            if len(parts) < 4:
                logger.warning(f"[Backend] Response format error: {parts}")
                return
            client_id, backend_identity, function_name, response = parts[:4]
            await self.frontend.send_multipart([client_id, b"", backend_identity, function_name, response])

    async def _heartbeat_monitor(self):
        while not self._stop:
            now = time.time()
            for tag, last in list(self.last_seen.items()):
                if now - last > self.HEARTBEAT_TIMEOUT:
                    with self._lock:
                        self.tag_to_identity.pop(tag, None)
                        self.last_seen.pop(tag, None)
                        logger.warning(f"[Router] Backend disconnection has been removed.: {tag}")
            await asyncio.sleep(self.HEARTBEAT_INTERVAL)

    async def stop(self):
        self._stop = True
        self.frontend.close(0)
        self.backend.close(0)
        self.ctx.term()
        cleanup_sockets()
        logger.info("🛑 RPC Router stop")


async def async_rpc_intelligent_router_main():
    router = AsyncRPCIntelligentRouter()
    await router.bind()
    try:
        await router.start()
    except asyncio.CancelledError:
        await router.stop()
    except KeyboardInterrupt:
        await router.stop()

def rpc_intelligent_router_main():
    run_asynchronous_function(async_rpc_intelligent_router_main())

