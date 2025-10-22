from abc import ABC,abstractmethod

from aitrados_api.trade_middleware.identity_mixin import IdentityMixin


class BackendService:
    """
    a_accept  must be implemented in your class

    """
    IDENTITY=IdentityMixin #implement  IDENTITY in your class
    def __init__(self):
        pass
    @abstractmethod
    async def a_accept(self,function_name:str,*args,**kwargs):
        raise NotImplementedError("Subclasses must implement this method")


