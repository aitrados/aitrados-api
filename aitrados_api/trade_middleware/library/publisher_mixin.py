import asyncio
import enum
import json
import threading
from asyncio import CancelledError
import zmq
import zmq.asyncio
from loguru import logger

from aitrados_api.common_lib.common import run_asynchronous_function
from aitrados_api.trade_middleware.trade_middleware_utils import set_pubsub_heartbeat_options
from aitrados_api.trade_middleware.client_adresss_detector import SubAddressDetector,IntelligentRouterContext

class AsyncPublisher:
    def __init__(self):
        self.ctx=None
        self.socket=None
        self.is_common_ctx=False
        self._lock=threading.Lock()
    async def _instance(self):
        with self._lock:
            self.addr=addr = SubAddressDetector.get_cached_type(is_async_context=True)#
            if addr.startswith("inproc://") and IntelligentRouterContext.async_pubsub:
                self.ctx = IntelligentRouterContext.async_pubsub
                self.is_common_ctx=True
            else:
                self.addr = addr = SubAddressDetector.get_cached_type()
                self.ctx  = zmq.asyncio.Context()
            self.socket = self.ctx.socket(zmq.PUB)


            set_pubsub_heartbeat_options(self.socket)
            self.socket.connect(addr)
            #print("public addr",self.addr)
    def send_topic(self,topic:bytes|str|enum.Enum,content:bytes|str|dict|list):
        run_asynchronous_function(self.a_send_topic(topic,content))



    async def a_send_topic(self,topic:bytes|str|enum.Enum,content:bytes|str|dict|list):
        if not self.socket or not self.ctx:
            await self._instance()

        #logger.info(f"[Publisher] {self.addr}  {topic}  ")
        if isinstance(topic, enum.Enum):
            topic = topic.value
        elif isinstance(topic,str):
            topic=topic.encode()



        if isinstance(content, str):
            content = content.encode()
        elif isinstance(content,dict|list):
            try:

                content=json.dumps(content,default=str).encode()
            except Exception as e:
                logger.warning(f"[Publisher] topic {topic} Json serialize error: {e}")
                content=str(content).encode()

        try:
             with self._lock:

                await self.socket.send_multipart([topic,content])
        except  CancelledError:
            print("[Publisher] CancelledError.")
        except KeyboardInterrupt:
            print("[Publisher] Interrupted.")
        except Exception as e:
            print(f"[Publisher] Error: {e}")
            pass


    def close(self):

        self.socket.close(linger=0)
        if not self.is_common_ctx:
            self.ctx.term()
            self.ctx=None
        self.socket=None