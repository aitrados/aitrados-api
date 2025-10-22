from loguru import logger
from aitrados_api.common_lib.subscribe_api.websocks_client import WebSocketClient
import traceback
from typing import List, Callable





class CallbackManage:
    #def __init__(self):

    __custom_show_subscribe_handle_msgs: List[Callable] = []
    __custom_event_handle_msgs: List[Callable] = []
    __custom_news_handle_msgs: List[Callable] = []
    __custom_auth_handle_msgs: List[Callable] = []
    __custom_handle_msgs: List[Callable] = []
    __custom_ohlc_handle_msgs: List[Callable] = []
    __custom_error_msgs: List[Callable] = []

    __custom_ohlc_chart_flow_streaming_callbacks: List[Callable] = []
    __custom_multi_timeframe_callbacks: List[Callable] = []





    @classmethod
    def add_custom_multi_timeframe_callback(self, func):
        self.__custom_multi_timeframe_callbacks.append(func)

    @classmethod
    def add_custom_ohlc_chart_flow_streaming_callback(self, func):
        self.__custom_ohlc_chart_flow_streaming_callbacks.append(func)
    @classmethod
    def add_custom_show_subscribe_handle_msg(self, func):
        self.__custom_show_subscribe_handle_msgs.append(func)
    @classmethod
    def add_custom_event_handle_msg(self, func):
        self.__custom_event_handle_msgs.append(func)
    @classmethod
    def add_custom_news_handle_msg(self, func):
        self.__custom_news_handle_msgs.append(func)
    @classmethod
    def add_custom_ohlc_handle_msg(self, func):
        self.__custom_ohlc_handle_msgs.append(func)
    @classmethod
    def add_custom_auth_handle_msg(self, func):
        self.__custom_auth_handle_msgs.append(func)
    @classmethod
    def add_custom_handle_msg(self, func):
        self.__custom_handle_msgs.append(func)

    @classmethod
    def add_custom_error_msgs(self, func):
        self.__custom_error_msgs.append(func)


    @classmethod
    def _default_multi_timeframe_callback(self, *args,**kwargs):
        #timeframe_item_manager.receive_data(name, data)
        for cb in self.__custom_multi_timeframe_callbacks:
            try:
                cb(*args,**kwargs)
            except Exception as e:
                traceback.print_exc()
    @classmethod
    def _default_show_subscribe_handle_msg(self, *args,**kwargs):
        for cb in self.__custom_show_subscribe_handle_msgs:
            try:
                cb(*args,**kwargs)
            except Exception as e:
                traceback.print_exc()


    @classmethod
    def _default_error_msg(self, *args,**kwargs):
        for cb in self.__custom_error_msgs:
            try:
                cb(*args,**kwargs)
            except Exception as e:
                traceback.print_exc()
    @classmethod
    def _default_ohlc_chart_flow_streaming_callback(self, *args,**kwargs):
        for cb in self.__custom_ohlc_chart_flow_streaming_callbacks:
            try:
                cb(*args,**kwargs)
            except Exception as e:
                traceback.print_exc()

    @classmethod
    def _default_event_handle_msg(self, client: WebSocketClient, data_list,*args,**kwargs):
        """Default callback for handling event messages"""
        for cb in self.__custom_event_handle_msgs:
            try:
                cb(client, data_list,*args,**kwargs)
            except Exception as e:
                logger.error(f"Error in custom event handler: {e}")
                traceback.print_exc()
    @classmethod
    def _default_news_handle_msg(self, client: WebSocketClient, data_list,*args,**kwargs):
        """Default callback for handling news messages"""
        for cb in self.__custom_news_handle_msgs:
            try:
                cb(client, data_list,*args,**kwargs)
            except Exception as e:
                logger.error(f"Error in custom news handler: {e}")
                traceback.print_exc()
    @classmethod
    def _default_ohlc_handle_msg(self, client: WebSocketClient, data_list,*args,**kwargs):
        """Default callback for handling ohlc messages"""
        for cb in self.__custom_ohlc_handle_msgs:
            try:
                cb(client, data_list,*args,**kwargs)
            except Exception as e:
                logger.error(f"Error in custom ohlc handler: {e}")
                traceback.print_exc()
    @classmethod
    def _default_auth_handle_msg(self, client: WebSocketClient, message,*args,**kwargs):
        """Default callback for handling authentication messages"""
        for cb in self.__custom_auth_handle_msgs:
            try:
                cb(client, message,*args,**kwargs)
            except Exception as e:
                logger.error(f"Error in custom auth handler: {e}")
                traceback.print_exc()
    @classmethod
    def _default_handle_msg(self, client: WebSocketClient, message,*args,**kwargs):
        """Default callback for handling general messages"""

        for cb in self.__custom_handle_msgs:
            try:
                cb(client, message,*args,**kwargs)
            except Exception as e:
                logger.error(f"Error in custom message handler: {e}")
                traceback.print_exc()