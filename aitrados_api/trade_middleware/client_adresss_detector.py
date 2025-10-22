import os
import tempfile
from abc import ABC
import platform
import hashlib

import zmq.asyncio
from aitrados_api.common_lib.common import get_env_value

from aitrados_api.trade_middleware.intelligent_router_address import FrontendIntelligentRouterAddress, \
    BackendIntelligentRouterAddress, SubIntelligentRouterAddress, PubIntelligentRouterAddress


class IntelligentRouterContext:
    async_rpc:zmq.asyncio.Context=None
    async_pubsub: zmq.asyncio.Context = None


class CommAddressDetector(ABC):
    _intelligent_router_address:FrontendIntelligentRouterAddress|BackendIntelligentRouterAddress|SubIntelligentRouterAddress|PubIntelligentRouterAddress=None
    _address_url = None
    _machine_id = None
    @classmethod
    def get__machine_id(cls):
        base = f"{platform.node()}-{platform.system()}"
        machine_id = hashlib.sha256(base.encode()).hexdigest()[:16]
        return machine_id

    @classmethod
    def delete_machine_id(cls):
        mid_file = os.path.join(tempfile.gettempdir(), "aitrados_mq_machine_id.txt")
        try:
            os.unlink(mid_file)
        except OSError:
            pass
    @classmethod
    def save_machine_id(cls):
        mid_file = os.path.join(tempfile.gettempdir(), "aitrados_mq_machine_id.txt")
        machine_id = cls.get__machine_id()
        with open(mid_file, "w") as f:
            f.write(machine_id)
    @classmethod
    def init(cls):
        if cls._machine_id is None:

            mid_file = os.path.join(tempfile.gettempdir(), "aitrados_mq_machine_id.txt")
            if os.path.exists(mid_file):
                with open(mid_file) as f:
                    cls._machine_id = f.read().strip()
                    pass


    @classmethod
    def detect(cls, peer_pid=None, peer_machine=None,is_async_context=True):
        cls.init()


        if is_async_context and peer_pid and peer_pid == get_env_value("TRADE_MIDDLEWARE_PID"):
            cls._address_url = cls._intelligent_router_address.INPROC
        elif platform.system() != "Windows" and  peer_machine and peer_machine == cls._machine_id:
            cls._address_url = cls._intelligent_router_address.IPC
        else:
            cls._address_url = cls._intelligent_router_address.TCP
        return cls._address_url

    @classmethod
    def get_cached_type(cls,is_async_context=False):
        if cls._address_url is None:
            peer_machine=cls.get__machine_id()
            peer_pid=os.getpid()
            cls.detect(peer_pid=peer_pid,peer_machine=peer_machine,is_async_context=is_async_context)
        return cls._address_url



class SubAddressDetector(CommAddressDetector):
    _intelligent_router_address=SubIntelligentRouterAddress
class PubAddressDetector(CommAddressDetector):
    _intelligent_router_address=PubIntelligentRouterAddress
class FrontendAddressDetector(CommAddressDetector):
    _intelligent_router_address=FrontendIntelligentRouterAddress
class BackendAddressDetector(CommAddressDetector):
    _intelligent_router_address=BackendIntelligentRouterAddress