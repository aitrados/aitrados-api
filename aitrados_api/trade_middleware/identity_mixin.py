from enum import Enum


class RpcFunctionMixin(Enum):
    @classmethod
    def get_array(cls):
        return [func.value for func in cls]

    @classmethod
    def get_names_array(cls):
        return [func.name for func in cls]

class ChannelMixin(Enum):
    @classmethod
    def get_array(cls):
        return [func.value for func in cls]
    @classmethod
    def get_names_array(cls):
        return [func.name for func in cls]
class IdentityMixin:
    backend_identity = "your_package_name"
    fun = RpcFunctionMixin
    channel = ChannelMixin