import asyncio
import threading
import traceback
from typing import Callable, Dict

import websockets
import json

from aitrados_api.common_lib.common import logger

from aitrados_api.common_lib.contant import SubscribeEndpoint


class WebSocketClientMixin:
    def _sync_to_async(self,func,*args,**kwargs):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None
        if loop and loop.is_running():
            loop.create_task(func(*args,**kwargs))
        else:
            asyncio.run(func(*args,**kwargs))
    async def _execute_callback(self,callback,*args,**kwargs):
        if not callback:
            return None
        if asyncio.iscoroutinefunction(callback):
            await callback( *args,**kwargs)
        else:
            callback(*args,**kwargs)
    async def callback(self,callback,msg,common_msg):
        await self._execute_callback(callback,self,msg)
        await self._execute_callback(self.handle_msg, self, common_msg)

    def check_subscription_topic(self,subscribe_type,topic:str)->bool:
        if not self.authorized:
            return False
        if topics:=self.all_subscribed_topics.get(subscribe_type):
            return topic in topics

        return False


class WebSocketClient(WebSocketClientMixin):
    RE_SUBSCRIBE_TYPES=[
        "ohlc",
        "news",
        "event"
    ]
    def __init__(self,secret_key,

                    is_re_subscribe:bool=True,
                    is_reconnect:bool=True,
                    handle_msg:Callable=None,
                    news_handle_msg:Callable=None,
                    event_handle_msg:Callable=None,
                    ohlc_handle_msg:Callable=None,
                    show_subscribe_handle_msg:Callable=None,
                    auth_handle_msg:Callable=None,
                    endpoint:str=SubscribeEndpoint.REALTIME,
                    debug:bool=False
                 ):


        self.secret_key = secret_key
        self.is_re_subscribe = is_re_subscribe
        self.is_reconnect = is_reconnect



        self.handle_msg = handle_msg
        self.news_handle_msg = news_handle_msg
        self.event_handle_msg = event_handle_msg
        self.ohlc_handle_msg = ohlc_handle_msg
        self.show_subscribe_handle_msg = show_subscribe_handle_msg
        self.auth_handle_msg = auth_handle_msg



        self.stop_event = None
        self.should_exit = False
        self.websocket = None
        self.authorized = False

        self.all_subscribed_topics:Dict[str,list]={}



        self.uri=None
        self.debug=debug

        self.init(endpoint)


    def init(self,endpoint):
        if not endpoint:
            endpoint=SubscribeEndpoint.REALTIME
        self.uri=f"{endpoint}/ws"
        if self.secret_key == "YOUR_SECRET_KEY":
            logger.error("Please set your actual API key instead of the placeholder YOUR_SECRET_KEY")
            raise ValueError("Please set your actual API key instead of the placeholder YOUR_SECRET_KEY")


    def close(self):


        self.should_exit = True
        if self.stop_event:
            self.stop_event.set()





    def subscribe_ohlc_1m(self, *topics: str):
        self._sync_to_async(self.a_subscribe_ohlc_1m,*topics)

    def subscribe_news(self, *topics: str):
        self._sync_to_async(self.a_subscribe_news,*topics)

    def subscribe_event(self, *topics: str):
        self._sync_to_async(self.a_subscribe_event,*topics)

    def unsubscribe_ohlc_1m(self, *topics: str):
        self._sync_to_async(self.a_unsubscribe_ohlc_1m,*topics)

    def unsubscribe_news(self, *topics: str):
        self._sync_to_async(self.a_unsubscribe_news,*topics)

    def unsubscribe_event(self, *topics: str):
        self._sync_to_async(self.a_unsubscribe_event,*topics)


    async def a_unsubscribe_ohlc_1m(self,*topics):
        if not topics or not self.authorized:
            return None
        subscribe_payload = {
            "message_type": "unsubscribe",
            "params": {
                "subscribe_type": "ohlc",
                "topics": topics
            }
        }
        await self.websocket.send(json.dumps(subscribe_payload))
        if self.debug:
            logger.info("--> sent ohlc unsubscribe request")
    async def a_unsubscribe_news(self,*topics):
        if not topics or not self.authorized:
            return None
        news_subscribe_payload={
            "message_type": "unsubscribe",
            "params": {
                "subscribe_type": "news",
                "topics": topics
                }
        }
        await self.websocket.send(json.dumps(news_subscribe_payload))
        if self.debug:
            logger.info("--> sent news unsubscribe request")

    async def a_unsubscribe_event(self,*topics):
        if not topics or not self.authorized:
            return None
        event_subscribe_payload = {
            "message_type": "unsubscribe",
            "params": {
                "subscribe_type": "event",
                "topics": topics
            }
        }
        await self.websocket.send(json.dumps(event_subscribe_payload))
        if self.debug:
            logger.info("--> sent event unsubscribe request")


    async def a_subscribe_ohlc_1m(self,*topics):
        if not topics or not self.authorized:
            return None
        subscribe_payload = {
            "message_type": "subscribe",
            "params": {
                "subscribe_type": "ohlc",
                "topics": topics
            }
        }
        await self.websocket.send(json.dumps(subscribe_payload))
        if self.debug:
            logger.info("--> sent ohlc sub request")



    async def a_subscribe_news(self,*topics):
        if not topics or not self.authorized:
            return None
        news_subscribe_payload={
            "message_type": "subscribe",
            "params": {
                "subscribe_type": "news",
                "topics": topics
                }
        }
        await self.websocket.send(json.dumps(news_subscribe_payload))
        if self.debug:
            logger.info("--> sent news sub request")

    async def a_subscribe_event(self,*topics):
        if not topics or not self.authorized:
            return None
        event_subscribe_payload = {
            "message_type": "subscribe",
            "params": {
                "subscribe_type": "event",
                "topics": topics
            }
        }
        await self.websocket.send(json.dumps(event_subscribe_payload))
        if self.debug:
            logger.info("--> sent event sub request")





    async def __auth_account(self):
        auth_payload = {
            "message_type": "authenticate",
            "params": {"secret_key": self.secret_key}
        }
        await self.websocket.send(json.dumps(auth_payload))

    async def __message_event(self):
        while not self.stop_event.is_set() and not self.should_exit:
            try:
                message_str = await asyncio.wait_for(self.websocket.recv(), timeout=1.0)
                message = json.loads(message_str)
                if message.get("message_type") == "event":
                    data_list = message.get("result", [])
                    if isinstance(data_list, list) and data_list:
                        await self.callback(self.event_handle_msg, data_list, message)
                elif message.get("message_type") == "news":
                    data_list = message.get("result", [])
                    if isinstance(data_list, list) and data_list:
                        await self.callback(self.news_handle_msg, data_list, message)
                elif message.get("message_type") == "ohlc":
                    data_list = message.get("result", [])
                    if isinstance(data_list, list) and data_list:
                        await self.callback(self.ohlc_handle_msg, data_list, message)
                elif message.get("message_type") == "show_subscribe":
                    if topic_data:=message.get('result', None):
                        for full_key in topic_data.keys():

                            key=full_key.split(":")[0]

                            self.all_subscribed_topics[key] = topic_data[full_key]
                        await self.callback(self.show_subscribe_handle_msg, topic_data, message)

                elif message.get("message_type") == "authenticate":
                    if message.get("result", {}).get("authenticated"):
                        if self.debug:
                            logger.success("--- ✅ Authentication successful ---")
                    else:
                        logger.error("--- ❌ Authentication failed ---")

                elif message.get("message_type") == "error":
                    await self._execute_callback(self.show_subscribe_handle_msg,message)
                    #logger.error(f"❌ SERVER ERROR: {message.get('message')} - {message.get('detail', '')}")

                else:
                    if self.debug:
                        logger.info(f"<-- receive smg: {message_str}")



            except asyncio.TimeoutError:
                continue
            except websockets.exceptions.ConnectionClosed as e:
                logger.error(f"Server closed the connection: {e}")
                break
            except Exception as e:
                logger.error(f"Error occurred while processing message: {e}")
                traceback.print_exc()
                break


    async def resubscribe_all(self):
        if not self.is_re_subscribe:
            return
        for subscribe_type in self.RE_SUBSCRIBE_TYPES:
            if topics:=self.all_subscribed_topics.get(subscribe_type):
                match subscribe_type:
                    case "ohlc":
                        await self.a_subscribe_ohlc_1m(*topics)
                    case "news":
                        await self.a_subscribe_news(*topics)
                    case "event":
                        await self.a_subscribe_event(*topics)
    async def __connect(self,is_reconnect=False):

        try:
            self.stop_event = asyncio.Event()
            if self.debug:
                logger.info(f"Connecting to WebSocket server: {self.uri}")

            async with websockets.connect(self.uri) as websocket:
                self.websocket = websocket
                if self.debug:
                    logger.success("--- ✅ Connect successfully ---")


                await self.__auth_account()
                if self.debug:
                    logger.info("--> Sent automatic authentication request")

                auth_response_str = await websocket.recv()
                auth_response = json.loads(auth_response_str)
                if self.debug:
                    logger.info(f"<-- Received authentication response: {auth_response_str}")

                if auth_response.get("result", {}).get("authenticated"):
                    if self.debug:
                        logger.success("--- ✅ Automatic authentication successful ---")
                    self.authorized = True
                    if  not (self.is_re_subscribe and is_reconnect):
                        await self.callback(self.auth_handle_msg,auth_response,auth_response)
                    await self.resubscribe_all()

                    await self.__message_event()


                else:
                    await self.callback(self.auth_handle_msg,auth_response,auth_response)
                    logger.error("--- ❌ Automatic authentication failed ---")



        except Exception as e:
            logger.error(f"Connection error: {e}")

        finally:
            self.authorized=False
            self.websocket = None
    def run(self,is_thread=False):
        if self.is_reconnect:
            if not is_thread:
                asyncio.run(self. run_with_reconnect())
            else:
                threading.Thread(target=lambda: asyncio.run(self.run_with_reconnect()), daemon=True).start()
        else:
            if not is_thread:
                asyncio.run(self.__connect())
            else:
                threading.Thread(target=lambda: asyncio.run(self.__connect()), daemon=True).start()




    async def run_with_reconnect(self,is_reconnect=False):

        while not self.should_exit:
            try:
                await self.__connect(is_reconnect)
            except Exception as e:
                logger.error(f"Connection error occurred: {e}")

            if not self.should_exit:
                await asyncio.sleep(5)
                if not self.should_exit:
                    if self.debug:
                        logger.info("Reconnecting...")
                    logger.info("*" * 50)
            is_reconnect=True