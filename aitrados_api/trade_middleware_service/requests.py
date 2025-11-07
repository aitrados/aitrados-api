from aitrados_api.trade_middleware.request import FrontendRequest, AsyncFrontendRequest
from aitrados_api.trade_middleware_service.trade_middleware_rpc_service import AitradosApiBackendService


def dataset_request(fun_name,*args,**kwargs):
    result = FrontendRequest.call_sync(
        AitradosApiBackendService.IDENTITY.backend_identity,
        fun_name, *args, **kwargs,
    )
    return result

async def a_dataset_request(fun_name,*args,**kwargs):
    result = await AsyncFrontendRequest.call_sync(
        AitradosApiBackendService.IDENTITY.backend_identity,
        fun_name, *args, **kwargs,
    )
    return result