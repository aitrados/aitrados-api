import json
import os
import signal
from time import sleep

import pandas as pd
import polars as pl
from aitrados_api import SubscribeEndpoint, ChartDataFormat
from aitrados_api import ClientConfig
from aitrados_api import DatasetClient
from aitrados_api import WebSocketClient
from aitrados_api import LatestOhlcChartFlowManager
from aitrados_api.common_lib.contant import IntervalName

api_config = ClientConfig(
    secret_key=os.getenv("AITRADOS_SECRET_KEY", "YOUR_SECRET_KEY"),
    debug=True
)
api_client = DatasetClient(config=api_config)


def show_subscribe_handle_msg(client: WebSocketClient, message):
    print("subscriptions", json.dumps(client.all_subscribed_topics))


ws_client = WebSocketClient(
    secret_key=os.getenv("AITRADOS_SECRET_KEY", "YOUR_SECRET_KEY"),
    show_subscribe_handle_msg=show_subscribe_handle_msg,
    endpoint=SubscribeEndpoint.REALTIME,
    debug=True
)


def latest_ohlc_chart_flow_callback(data: str | list | dict | pd.DataFrame | pl.DataFrame):
    if isinstance(data, list):
        print("Received data:", json.dumps(data[-2:], indent=2))
    else:
        print("Received data:", data)


latest_ohlc_chart_flow_manager = LatestOhlcChartFlowManager(
    latest_ohlc_chart_flow_callback=latest_ohlc_chart_flow_callback,
    api_client=api_client,
    ws_client=ws_client,
    limit=150,
    data_format=ChartDataFormat.DICT
)

is_close = False


def signal_handler(sig, frame):
    ws_client.close()
    global is_close
    is_close = True


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    ws_client.run(is_thread=True)

    latest_ohlc_chart_flow_manager.add_item("crypto:global:btcusd", IntervalName.M1)
    '''
    latest_ohlc_chart_flow_manager.add_item("crypto:global:btcusd", IntervalName.M3)
    latest_ohlc_chart_flow_manager.add_item("crypto:global:btcusd", IntervalName.M5)
    latest_ohlc_chart_flow_manager.add_item("crypto:global:btcusd", IntervalName.M10)
    latest_ohlc_chart_flow_manager.add_item("crypto:global:btcusd", IntervalName.M15)
    latest_ohlc_chart_flow_manager.add_item("crypto:global:btcusd", IntervalName.M60)
    latest_ohlc_chart_flow_manager.add_item("crypto:global:btcusd", IntervalName.M120)
    latest_ohlc_chart_flow_manager.add_item("crypto:global:btcusd", IntervalName.M240)
    latest_ohlc_chart_flow_manager.add_item("crypto:global:btcusd", IntervalName.WEEK)
    latest_ohlc_chart_flow_manager.add_item("crypto:global:btcusd", IntervalName.MON)
    '''
    while not is_close:
        sleep(2)
    latest_ohlc_chart_flow_manager.remove_item("crypto:global:btcusd", IntervalName.M1)
    '''
    latest_ohlc_chart_flow_manager.remove_item("crypto:global:btcusd", IntervalName.M3)
    latest_ohlc_chart_flow_manager.remove_item("crypto:global:btcusd", IntervalName.M5)
    latest_ohlc_chart_flow_manager.remove_item("crypto:global:btcusd", IntervalName.M10)
    latest_ohlc_chart_flow_manager.remove_item("crypto:global:btcusd", IntervalName.M15)
    latest_ohlc_chart_flow_manager.remove_item("crypto:global:btcusd", IntervalName.M60)
    latest_ohlc_chart_flow_manager.remove_item("crypto:global:btcusd", IntervalName.M120)
    latest_ohlc_chart_flow_manager.remove_item("crypto:global:btcusd", IntervalName.M240)
    latest_ohlc_chart_flow_manager.remove_item("crypto:global:btcusd", IntervalName.WEEK)
    latest_ohlc_chart_flow_manager.remove_item("crypto:global:btcusd", IntervalName.MON)
    '''
