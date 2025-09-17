import json
import os
import signal


from aitrados_api.common_lib.common import logger

from aitrados_api import SubscribeEndpoint
from aitrados_api import WebSocketClient


def handle_msg(client: WebSocketClient, message):
    # print("Received message:", message)
    pass


def news_handle_msg(client: WebSocketClient, data_list):
    for record in data_list:
        symbol = f"{record.get('asset_schema')}:{record.get('country_iso_code')}:{record.get('underlying_name')}"
        string = f"news:{symbol} --> {record.get('published_date')} --> {record.get('title')}"
        logger.info(string)


def event_handle_msg(client: WebSocketClient, data_list):
    for record in data_list:
        symbol = f"{record.get('country_iso_code')}:{record.get('event_code')}:{record.get('preview_interval')}"
        string = f"event:{symbol} --> {record.get('event_timestamp')}"
        logger.info(string)


def ohlc_handle_msg(client: WebSocketClient, data_list):
    count = len(data_list)
    first_asset_schema = data_list[0].get('asset_schema', 'N/A')

    logger.info(
        f"Real-time data: Received 'ohlc_data' containing {count} records (asset type: {first_asset_schema}) {data_list[0].get('time_key_timestamp', 'N/A')}")


def show_subscribe_handle_msg(client: WebSocketClient, message):
    #logger.info(f"✅ Subscription status: {message}")

    print("subscriptions",json.dumps(client.all_subscribed_topics))


def auth_handle_msg(client: WebSocketClient, message):
    if not client.authorized:
        return

    client.subscribe_news("STOCK:US:*", "CRYPTO:GLOBAL:*", "FOREX:GLOBAL:*")
    client.subscribe_ohlc_1m("STOCK:US:*", "CRYPTO:GLOBAL:*", "FOREX:GLOBAL:*")
    client.subscribe_event('US:*', 'CN:*', 'UK:*', 'EU:*', 'AU:*', 'CA:*', 'DE:*', 'FR:*', 'JP:*', 'CH:*')


client = WebSocketClient(
    secret_key=os.getenv("AITRADOS_SECRET_KEY","YOUR_SECRET_KEY"),
    is_reconnect=True,

    handle_msg=handle_msg,
    news_handle_msg=news_handle_msg,
    event_handle_msg=event_handle_msg,
    ohlc_handle_msg=ohlc_handle_msg,
    show_subscribe_handle_msg=show_subscribe_handle_msg,
    auth_handle_msg=auth_handle_msg,
    endpoint=SubscribeEndpoint.DELAYED,
    debug=True
)


def signal_handler(sig, frame):
    client.close()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    client.run(is_thread=False)
    '''
    while True:
        sleep(2)
    '''
