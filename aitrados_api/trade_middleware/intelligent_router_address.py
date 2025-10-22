import os
import getpass
from abc import ABC
import platform
class IntelligentRouterAddress(ABC):
    TCP = None
    IPC = None
    INPROC = None
    @classmethod
    def get_array(cls):
        if platform.system() != "Windows":
            return [cls.TCP, cls.IPC, cls.INPROC]
        else:
            return [cls.TCP, cls.INPROC]

class FrontendIntelligentRouterAddress(IntelligentRouterAddress):
    TCP = "tcp://127.0.0.1:51591"
    IPC = f"ipc:///tmp/aitrados_frontend_{getpass.getuser()}.sock"
    INPROC = "inproc://aitrados_frontend"
class BackendIntelligentRouterAddress(IntelligentRouterAddress):
    TCP = "tcp://127.0.0.1:51592"
    IPC = f"ipc:///tmp/aitrados_backend_{getpass.getuser()}.sock"
    INPROC = "inproc://aitrados_backend"

class SubIntelligentRouterAddress(IntelligentRouterAddress):
    TCP = "tcp://127.0.0.1:51593"
    IPC = f"ipc:///tmp/aitrados_sub_{getpass.getuser()}.sock"
    INPROC = "inproc://aitrados_sub"
class PubIntelligentRouterAddress(IntelligentRouterAddress):
    TCP = "tcp://127.0.0.1:51594"
    IPC = f"ipc:///tmp/aitrados_pub_{getpass.getuser()}.sock"
    INPROC = "inproc://aitrados_pub"



def cleanup_sockets():
    from aitrados_api.trade_middleware.client_adresss_detector import CommAddressDetector
    import glob
    user = getpass.getuser()
    pattern = f"/tmp/aitrados_*_{user}.sock"
    for sock_file in glob.glob(pattern):
        try:
            os.unlink(sock_file)
        except OSError:
            pass
    CommAddressDetector.delete_machine_id()