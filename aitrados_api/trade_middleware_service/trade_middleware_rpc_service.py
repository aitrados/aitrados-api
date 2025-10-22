from pydantic import BaseModel

from aitrados_api.common_lib.any_list_data_to_format_data import AnyToFormat
from aitrados_api.common_lib.response_format import ErrorResponse, UnifiedResponse
from aitrados_api.trade_middleware_service.trade_middleware_identity import aitrados_api_identity
from aitrados_api.trade_middleware.backend_service import BackendService
from aitrados_api.trade_middleware_service.trade_middleware_service_instance import AitradosApiServiceInstance



class AitradosApiBackendService(BackendService):
    ALL_FUNCTION_LIST = aitrados_api_identity.fun.get_array()
    YIELD_API_CLIENT_FUNCTION_LIST=[
        aitrados_api_identity.fun.OHLCS.value,
        aitrados_api_identity.fun.SEARCH_OPTION.value,
        aitrados_api_identity.fun.STOCK_CORPORATE_ACTION_LIST.value,
        aitrados_api_identity.fun.EVENT_LIST.value,
        aitrados_api_identity.fun.HOLIDAY_LIST.value,
        aitrados_api_identity.fun.NEWS_LIST.value,
    ]
    WS_FUNCTION_LIST=[
        aitrados_api_identity.fun.SUBSCRIBE_NEWS.value,
        aitrados_api_identity.fun.SUBSCRIBE_OHLC_1M.value,
        aitrados_api_identity.fun.SUBSCRIBE_EVENT.value,

        aitrados_api_identity.fun.UNSUBSCRIBE_NEWS.value,
        aitrados_api_identity.fun.UNSUBSCRIBE_OHLC_1M.value,
        aitrados_api_identity.fun.UNSUBSCRIBE_EVENT.value,
        aitrados_api_identity.fun.RESUBSCRIBE_ALL.value,
        aitrados_api_identity.fun.ALL_SUBSCRIBED_TOPICS.value,

    ]

    LATEST_OHLC_CHART_FLOW_FUNCTION_LIST=[
        aitrados_api_identity.fun.ADD_LATEST_OHLC_CHART_FLOW_ITEM.value,
        aitrados_api_identity.fun.ADD_LATEST_OHLC_CHART_FLOW_ITEM.value,
        aitrados_api_identity.fun.ADD_LATEST_OHLC_CHART_FLOW_ITEM_OR_GET_DATA.value,
    ]

    LATEST_OHLC_MULTI_TIMEFRAME_FUNCTION_LIST=[
        aitrados_api_identity.fun.ADD_LATEST_OHLC_MULTI_TIMEFRAME_ITEM.value,
        aitrados_api_identity.fun.REMOVE_LATEST_OHLC_MULTI_TIMEFRAME_ITEM.value,
        aitrados_api_identity.fun.ADD_LATEST_OHLC_MULTI_TIMEFRAME_ITEM_OR_GET_DATA.value,
    ]
    IDENTITY = aitrados_api_identity
    def __init__(self):
        super().__init__()
    async def a_accept(self, function_name: str, *args, **kwargs):
        if not AitradosApiServiceInstance.latest_ohlc_multi_timeframe_manager:
            from aitrados_api.universal_interface.aitrados_instance import latest_ohlc_multi_timeframe_manager_instance
            pass



        if function_name not in self.ALL_FUNCTION_LIST:
            return ErrorResponse(
                message=F"Unknown request '{function_name}'").model_dump_json()

        try:
            if function_name in self.WS_FUNCTION_LIST:
                return await self.__ws_client_request(function_name, *args, **kwargs)
            elif function_name in self.LATEST_OHLC_CHART_FLOW_FUNCTION_LIST:
                return await self.__latest_ohlc_chart_flow_request(function_name, *args, **kwargs)
            elif function_name in self.LATEST_OHLC_MULTI_TIMEFRAME_FUNCTION_LIST:
                return await self.__latest_ohlc_multi_timeframe_request(function_name, *args, **kwargs)

            result=await self.__api_client_request(function_name, *args, **kwargs)
        except Exception as e:
            erro="ensure function_name is correct and args/kwargs are valid. [find all functions module file:aitrados_api/trade_middleware_service/trade_middleware_identity.py]"

            return ErrorResponse(message=F"Error: {e}.\n{erro}").model_dump_json()
        return result








    async def __latest_ohlc_multi_timeframe_request(self, function_name: str, *args, **kwargs):
        target= AitradosApiServiceInstance.latest_ohlc_multi_timeframe_manager
        match function_name:
            case aitrados_api_identity.fun.ADD_LATEST_OHLC_MULTI_TIMEFRAME_ITEM.value:
                final_method = getattr(target, "add_item")
            case aitrados_api_identity.fun.REMOVE_LATEST_OHLC_MULTI_TIMEFRAME_ITEM.value:
                final_method = getattr(target, "remove_item")
            case aitrados_api_identity.fun.ADD_LATEST_OHLC_MULTI_TIMEFRAME_ITEM_OR_GET_DATA.value:
                final_method = getattr(target, "add_item_or_get_data")
                if kwargs.get("to_format") not in AnyToFormat.get_serialized_array():
                    kwargs["to_format"]=AnyToFormat.CSV
            case __:
                return ErrorResponse(
                    message=f"Unknown request '{function_name}' latest_ohlc_multi_timeframe only support function 'add_item','remove_item'. ").model_dump_json()

        result = final_method(*args, **kwargs)
        if hasattr(result, '__await__'):
            result = await result
        if isinstance(result,UnifiedResponse|ErrorResponse):
            return result.model_dump_json()
        return UnifiedResponse(result=result).model_dump_json()


    async def __latest_ohlc_chart_flow_request(self, function_name: str, *args, **kwargs):
        target = AitradosApiServiceInstance.latest_ohlc_chart_flow_manager

        match function_name:
            case aitrados_api_identity.fun.ADD_LATEST_OHLC_CHART_FLOW_ITEM.value:
                final_method = getattr(target, "add_item")
            case aitrados_api_identity.fun.REMOVE_LATEST_OHLC_CHART_FLOW_ITEM.value:
                final_method = getattr(target, "remove_item")
            case aitrados_api_identity.fun.ADD_LATEST_OHLC_CHART_FLOW_ITEM_OR_GET_DATA.value:
                final_method = getattr(target, "add_item_or_get_data")
                if kwargs.get("to_format") not in AnyToFormat.get_serialized_array():
                    kwargs["to_format"]=AnyToFormat.CSV


            case __:
                return ErrorResponse(
                    message=f"Unknown request '{function_name}' latest_ohlc_chart_flow only support function 'add_item','remove_item','add_item_or_get_data'. ").model_dump_json()


        result= final_method(*args, **kwargs)
        if hasattr(result, '__await__'):
            result = await result

        if isinstance(result,UnifiedResponse|ErrorResponse):
            return result.model_dump_json()

        return UnifiedResponse(result=result).model_dump_json()

    async def __api_client_request(self, function_name: str, *args, **kwargs):
        api_client = AitradosApiServiceInstance.api_client


        # Get objects by attribute name in turn
        target = api_client
        parts = function_name.split(".")

        # Iterate through all sections except the last one and get the nested objects
        for fun_name in parts[:-1]:
            target = getattr(target, fun_name)

        # Get the final method
        final_method = getattr(target, parts[-1])
        if function_name not in self.YIELD_API_CLIENT_FUNCTION_LIST:
            result:BaseModel = final_method(*args, **kwargs)
            if hasattr(result, '__await__'):
                result = await result
        else:
            async for data in final_method(*args, **kwargs):
                result:BaseModel = data
                break

        return result.model_dump_json()

    async def __ws_client_request(self, function_name: str, *args, **kwargs):


        target = AitradosApiServiceInstance.ws_client
        parts = function_name.split(".")

        # Iterate through all sections except the last one and get the nested objects
        for fun_name in parts[:-1]:
            target = getattr(target, fun_name)

        # Get the final method
        final_method = getattr(target, parts[-1])
        result = final_method(*args, **kwargs)
        if hasattr(result, '__await__'):
            result = await result

        return UnifiedResponse(result=result).model_dump_json()

