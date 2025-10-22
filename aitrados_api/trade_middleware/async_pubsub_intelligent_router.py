import asyncio
import threading

import zmq
import zmq.asyncio
from loguru import logger
from aitrados_api.common_lib.common import run_asynchronous_function, is_debug
from aitrados_api.trade_middleware.intelligent_router_address import SubIntelligentRouterAddress, PubIntelligentRouterAddress
from aitrados_api.trade_middleware.trade_middleware_utils import set_pubsub_heartbeat_options

from aitrados_api.trade_middleware.client_adresss_detector import IntelligentRouterContext
class AsyncPubsubIntelligentRouter:
    def __init__(self):
        self.sync_ctx = None
        self.frontend = None
        self.backend = None
        self.control_frontend = None
        self.control_backend = None
        self.running = False
        self.proxy_thread = None


    async def start(self):
        if self.running:
            logger.warning("[Pubsub Router] Already running")
            return


        self.sync_ctx = zmq.asyncio.Context()
        IntelligentRouterContext.async_pubsub = self.sync_ctx
        self.frontend = self.sync_ctx.socket(zmq.XSUB)
        self.backend = self.sync_ctx.socket(zmq.XPUB)
        self.control_frontend = self.sync_ctx.socket(zmq.PAIR)
        self.control_backend = self.sync_ctx.socket(zmq.PAIR)

        set_pubsub_heartbeat_options(self.backend)
        set_pubsub_heartbeat_options(self.frontend)

        for addr in SubIntelligentRouterAddress.get_array():
            try:
                self.frontend.bind(addr)
            except Exception as e:
                logger.error(f"[PUBSUB] Binding failed {addr}: {e}")
                exit(0)

        for addr in PubIntelligentRouterAddress.get_array():
            try:
                self.backend.bind(addr)
            except Exception as e:
                logger.error(f"[PUBSUB] Binding failed {addr}: {e}")
                exit(0)

        self.control_frontend.bind("inproc://pubsub_router_control")
        self.control_backend.connect("inproc://pubsub_router_control")

        self.running = True
        logger.info("📡 Pubsub Router Started")
        if is_debug():
            logger.debug(f"                         Sub addr:{SubIntelligentRouterAddress.get_array()}")
            logger.debug(f"                         Pub addr:{PubIntelligentRouterAddress.get_array()}")


        self.proxy_thread = threading.Thread(target=self._run_proxy_sync, daemon=True)
        self.proxy_thread.start()

    def _run_proxy_sync(self):

        try:
            zmq.proxy_steerable(
                self.frontend,
                self.backend,
                None,
                self.control_frontend
            )
            logger.info("[Pubsub Router] Proxy Normal exit")
        except zmq.ContextTerminated:
            logger.info("[Pubsub Router] Context Terminated")
        except Exception as e:
            logger.error(f"[Pubsub Router] Proxy mistake: {e}")

    async def stop(self):

        if not self.running:
            logger.warning("[Pubsub Router] Not running")
            return

        logger.info("[Pubsub Router] Stopping...")

        try:

            if self.control_backend:
                self.control_backend.send(b"TERMINATE")
                await asyncio.sleep(0.2)


            if self.proxy_thread and self.proxy_thread.is_alive():
                self.proxy_thread.join(timeout=2.0)
                if self.proxy_thread.is_alive():
                    logger.warning("[Pubsub Router] Proxy The thread failed to terminate in time")

        except Exception as e:
            logger.error(f"[Pubsub Router] Error while stopping: {e}")
        finally:
            await self.cleanup()

    async def cleanup(self):
        try:
            if self.control_backend:
                self.control_backend.close(linger=0)
                self.control_backend = None

            if self.control_frontend:
                self.control_frontend.close(linger=0)
                self.control_frontend = None

            if self.frontend:
                self.frontend.close(linger=0)
                self.frontend = None

            if self.backend:
                self.backend.close(linger=0)
                self.backend = None

            if self.sync_ctx:
                self.sync_ctx.term()
                self.sync_ctx = None

            self.running = False
            logger.info("[Pubsub Router] stop")
        except Exception as e:
            logger.error(f"[Pubsub Router] Error during cleanup: {e}")

    async def run(self):
        await self.start()
        try:
            while self.running:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("[Pubsub Router] Manual interrupt")
        finally:
            await self.stop()


_router_instance:AsyncPubsubIntelligentRouter = None


def pubsub_intelligent_router_main():
    global _router_instance
    _router_instance = AsyncPubsubIntelligentRouter()

    try:
        run_asynchronous_function(_router_instance.run())
    except KeyboardInterrupt:
        logger.info("Manual interrupt, closing...")


def stop_pubsub_router():
    global _router_instance
    if _router_instance and _router_instance.running:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(_router_instance.stop())
        finally:
            loop.close()

