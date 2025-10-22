import json
from abc import ABC

import zmq
import zmq.asyncio
import asyncio

from loguru import logger

from aitrados_api.trade_middleware.backend_service import BackendService
from aitrados_api.trade_middleware.client_adresss_detector import BackendAddressDetector, IntelligentRouterContext

class AsyncBackendResponseMixin(ABC):
    def __init__(self, backend_service:BackendService,backend_identity:str=None):
        if not backend_identity:
            backend_identity=backend_service.IDENTITY.backend_identity

        self.backend_identity = f"{backend_identity}".encode()
        self.backend_service=backend_service
        self.ctx: zmq.asyncio.Context = None
        self.socket = None


    async def init(self):

        addr = BackendAddressDetector.get_cached_type(is_async_context=True)
        if addr.startswith("inproc://"):
            self.ctx=IntelligentRouterContext.async_rpc
        else:
            self.ctx = zmq.asyncio.Context()
        self.socket = self.ctx.socket(zmq.DEALER)

        self.socket.setsockopt(zmq.IDENTITY, self.backend_identity)

        self.socket.connect(addr)

        # 向路由器注册自己
        await self.register_to_router()

        # 启动心跳和消息处理
        asyncio.create_task(self.send_heartbeat())
        await self.handle_requests()


    async def register_to_router(self):
        """向路由器注册服务"""

        await self.socket.send_multipart([
            b"",  # 添加空帧分隔符
            b"REGISTER",
            self.backend_identity
        ])
        logger.debug(f"RPC backend '{self.backend_identity.decode()}' is submitting to Register RPC Service")



    async def send_heartbeat(self):
        """定期发送心跳"""

        while True:
            await asyncio.sleep(5)  # 每5秒发送心跳
            try:
                await self.socket.send_multipart([
                    b"",
                    b"HEARTBEAT",
                    self.backend_identity
                ])
            except Exception as e:
                print(f"Heartbeat sending failed: {e}")

    async def handle_requests(self):
        while True:
            try:
                # receive data：[empty, client_id, backend_name, function_name, args,kwargs]
                msg = await self.socket.recv_multipart()
                if len(msg) >= 5:
                    empty, client_id, backend_name, function_name, params = msg[:5]

                    # 处理请求
                    response = await self.process_request(
                        function_name.decode('utf-8'),
                        params.decode('utf-8'),


                    )

                    # send response：[empty, client_id, backend_name, function_name, response]
                    await self.socket.send_multipart([
                        b"",  # 空帧
                        client_id,
                        backend_name,
                        function_name,
                        response.encode()
                    ])

            except Exception as e:

                print(f"Failed to process the request: {e}")
                raise

    async def process_request(self, function_name: str,params:str):
        params_dict=json.loads(params)
        args=params_dict.get("args",[])
        kwargs=params_dict.get("kwargs", {})
        response= await self.backend_service.a_accept(function_name, *args, **kwargs)
        if not response:
            raise Exception(f"RPC response can not be None: {self.backend_identity.decode()}.{function_name}({args},{kwargs})")
        return response