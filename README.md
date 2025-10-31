# aitrados-dataset-api
[![PyPI version](https://badge.fury.io/py/aitrados-api.svg)](https://badge.fury.io/py/aitrados-api)
[![Python Support](https://img.shields.io/pypi/pyversions/aitrados-api.svg)](https://pypi.org/project/aitrados-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

`aitrados-dataset-api` is more than a Python client; it is a powerful framework engineered for professional, AI-driven quantitative trading. We move beyond simple data fetching to solve the most complex and time-consuming data management challenges, allowing you to focus exclusively on strategy development and alpha generation.

Our core philosophy is to provide a seamless data engine that elevates your analysis from a single asset to a panoramic view of the entire market ecosystem. By integrating **Effortless Real-Time OHLC Chart Flows**, **Professional-Grade Multi-Symbol, Multi-Timeframe (MSMTF) Time Alignment**, and **AI-Powered Fusion Analysis** (combining K-line, news, and economic events), `aitrados-dataset-api` provides an unprecedented data foundation for sophisticated algorithmic trading.

**Github**: [https://github.com/aitrados/aitrados-api](https://github.com/aitrados/aitrados-api)

**EXAMPLES**: [https://github.com/aitrados/aitrados-api/tree/main/examples](https://github.com/aitrados/aitrados-api/tree/main/examples)

**DOCS**: [https://docs.aitrados.com/en/docs/api/quickstart/](https://docs.aitrados.com/en/docs/api/quickstart/)  

**OFFLINE DOCS**: [https://github.com/aitrados/aitrados-api/tree/main/docs/api](https://github.com/aitrados/aitrados-api/tree/main/docs/api)  

**FREE GAIN SECRET KEY**:[https://www.aitrados.com/](https://www.aitrados.com/)  


## Core Advantages: Redefining Your Trading Dataflow

In quantitative trading, data is the source of alpha, but data management is often the biggest obstacle. `aitrados-dataset-api` liberates you from the complex "data plumbing."

*   🚀 **Effortless Real-Time OHLC Chart Flow**
    *   **The Pain Point**: Maintaining a live, rolling, fixed-length OHLC chart (e.g., the latest 150 candles) is notoriously difficult. Developers wrestle with initial history loading, real-time WebSocket updates, managing the unclosed "live" candle, and handling the precise rollover logic—a process that is complex and highly prone to errors.
    *   **The AiTrados Solution**: Our `LatestOhlcChartFlowManager` completely automates this entire workflow. With a single command, you get a perfectly aligned, always-current rolling chart data stream. We handle all the underlying complexity, so you can immediately focus on strategy implementation.

*   🌐 **Professional-Grade Multi-Symbol, Multi-Timeframe (MSMTF) Alignment**
    *   **The Pain Point**: Advanced strategies like pairs trading, arbitrage, and hedging require analyzing multiple symbols across different timeframes simultaneously. Manually aligning OHLC data from these disparate sources to ensure perfect timestamp synchronization is a monumental challenge.
    *   **The AiTrados Solution**: Our MSMTF framework `LatestOhlcMultiTimeframeManager` is a philosophy built for professional trading. It doesn't just provide multi-symbol data; its core strength lies in ensuring **precise time alignment** across all datasets. This empowers you to build sophisticated cross-market models, identify leader-follower relationships, and capture fleeting arbitrage opportunities with confidence.

*   🧩 **Designed for AI-Powered Fusion Analysis**
    *   Seamlessly integrate naked K-line technical analysis, real-time news events, and macroeconomic data into a single, unified data source. This provides the clean, synchronized, and rich input required to train complex AI models and execute time-sensitive trading decisions.

## Feature Overview

*   **Advanced Real-Time Capabilities via WebSocket:**
    *   Fully managed, real-time rolling OHLC chart flows.
    *   Time-aligned data streams for multiple symbols and timeframes.
    *   Real-time news feeds and economic event alerts.
    *   Economic event support preview_interval and realtime alerts.for example alert before 5/10/30/60 minutes 1 DAY,2 WEEKS.

*   **Comprehensive Historical Data via HTTP API:**
    *   OHLCV data with extensive multi-timeframe support.
    *   Reference data for symbols (stocks, crypto, forex,option,futures , etc.).
    *   Options chains and expiration dates.
    *   Corporate actions (splits, dividends).
    *   Macroeconomic calendars and event history.
    *   Global trading holiday schedules.
    *   Vast archives of historical financial news.


## trade middleware (LOCAL RPC & SUB/PUB )

We introduce zeromq middleware, you can completely split complex strategies into modules and programs. Through the middleware to implement complex communication data calls
[SEE DOCS](https://docs.aitrados.com/en/docs/api/trade_middleware/overview/)  

## Installation

You can install this library using pip:
```bash
pip install aitrados-api
```
### From source
```bash
git clone https://github.com/aitrados/aitrados-api.git
cd aitrados-api
pip install -r requirements.txt
#pip install -e .
```


## Usage

### Super easy startup with rpc pubsub
see https://docs.aitrados.com/en/docs/api/trade_middleware/run_trade_middleware/
```python
import time
from aitrados_api.common_lib.common import load_env_file
from aitrados_api.common_lib.contant import SubscribeEndpoint, SchemaAsset, IntervalName
from aitrados_api.common_lib.subscribe_api.websocks_client import WebSocketClient
from aitrados_api.universal_interface.callback_manage import CallbackManage
from aitrados_api.universal_interface.aitrados_instance import api_client_instance,ws_client_instance,latest_ohlc_multi_timeframe_manager_instance,latest_symbol_charting_manager_instance
from aitrados_api.universal_interface.trade_middleware_instance import AitradosTradeMiddlewareInstance
load_env_file(".env", override=True)
if __name__ == "__main__":
    AitradosTradeMiddlewareInstance.run_all()
    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("closing...")
```

### HTTP API - Get Historical Data

You need to use your API key to initialize the `DatasetClient`.

```python
import asyncio
import os

from aitrados_api import DatasetClient
from aitrados_api import ClientConfig, RateLimitConfig
from aitrados_api import SchemaAsset, IntervalName


async def run_async_example():
    config = ClientConfig(
        secret_key=os.getenv("AITRADOS_SECRET_KEY", "YOUR_SECRET_KEY"),
        timeout=30,
        max_retries=1000,
        rate_limit=RateLimitConfig(
            daily_limit=100000,
            requests_per_second=2,
            requests_per_minute=30
        ),
        debug=True
    )

    client = DatasetClient(config=config)
    params = {
        "schema_asset": SchemaAsset.CRYPTO,
        "country_symbol": "GLOBAL:BTCUSD",
        "interval": IntervalName.M60,
        "from_date": "2025-07-18T00:00:00+00:00",
        "to_date": "2025-10-05T23:59:59+00:00",
        "format": "json",
        "limit": 30
    }
    # ***************************************OHLC DATA***************************#
    '''
    # Get historical OHLC data asynchronously
    async for ohlc in client.ohlc.a_ohlcs(**params):
        print(ohlc)
    '''

    # Get latest OHLC data asynchronously. use for real-time data
    ohlc_latest = await client.ohlc.a_ohlcs_latest(**params)
    print(ohlc_latest)

    # ***************************************symbol reference***************************#
    '''
    # Get symbol reference asynchronously
    stock_reference = await client.reference.a_reference(schema_asset=SchemaAsset.STOCK, country_symbol="US:TSLA")
    crypto_reference = await client.reference.a_reference(schema_asset=SchemaAsset.CRYPTO, country_symbol="GLOBAL:BTCUSD")
    forex_reference = await client.reference.a_reference(schema_asset=SchemaAsset.FOREX, country_symbol="GLOBAL:EURUSD")
    '''
    # ***************************************OPTIONS INFORMATION***************************#
    '''
    # Get options information asynchronously
    async for options in client.reference.a_search_option(schema_asset=SchemaAsset.STOCK, country_symbol="US:spy",
                                                          option_type="call", moneyness="in_the_money",
                                                          ref_asset_price=450.50, limit=100):
        print(options)
    '''

    '''
    # Get options expiration date list asynchronously
    expiration_date_list = await client.reference.a_options_expiration_date_list(schema_asset=SchemaAsset.STOCK,
                                                                                 country_symbol="US:SPY")
    print(expiration_date_list)
    '''
    # ***************************************stock corporate action***************************#
    '''
    # Get stock corporate action list asynchronously
    async for actions in client.reference.a_stock_corporate_action_list(country_symbol="US:TSLA",
                                                                         from_date="2020-08-18",
                                                                         action_type="split", limit=100):
        print(actions)
    '''
    # ***************************************economic event***************************#
    '''
    # Get economic event codes of all countries asynchronously
    event_codes = await client.economic.a_event_codes(country_iso_code="US")
    print(event_codes)
    '''

    '''
    # Get economic event list asynchronously
    async for event_list in client.economic.a_event_list(country_iso_code="US", limit=5):
        print(event_list)
    '''
    '''
    # Get economic event by date asynchronously
    event = await client.economic.a_event()
    print(event)
    '''

    '''
    # Get economic latest event list asynchronously
    latest_events = await client.economic.a_latest_events(country_iso_code="us",date_type="upcoming")
    print(latest_events)
    '''

    # ***************************************holiday***************************#
    '''
    # Get holiday list asynchronously
    async for holiday_list in client.holiday.a_holiday_list(full_symbol="stock:US:*", from_date="2023-01-01",
                                                            to_date="2026-12-31", limit=100):
        print(holiday_list)
    '''
    '''
    # Get holiday codes of all countries asynchronously
    holiday_codes = await client.holiday.a_holiday_codes()
    print(holiday_codes)
    '''
    # ***************************************news***************************#
    '''
    # Get news list asynchronously
    async for news_list in client.news.a_news_list(full_symbol="stock:US:TSLA", from_date="2025-07-01",
                                                  to_date="2025-12-31", limit=100):
        print(news_list)
    '''

    '''
    # Get latest news asynchronously. use for real-time data
    news_latest = await client.news.a_news_latest(full_symbol="stock:US:TSLA", limit=5)
    print(news_latest)
    '''
    client.close()
if __name__ == "__main__":
    asyncio.run(run_async_example())
```


### WebSocket API - Subscribe to Real-time Data

With the `WebSocketClient`, you can subscribe to various real-time data streams.

```python
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


```

### LATEST REAL-TIME OHLC PRICE CHART FLOW STREAMS EXAMPLE

With the `WebSocketClient` and `DatasetClient`, you can get the latest ohlc chart flow streams.
```python
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

```
### Example: Real-Time OHLC Price Chart Streams with MTF (Multiple-Timeframes) and MSMTF (Multiple-Symbols-Multiple-Timeframes) Alignment

Thanks to the unique time-series architecture used by AiTrados, we offer a distinct advantage in the precise temporal alignment of market data. This allows for the seamless implementation of both Multi-Timeframe (MTF) and Multi-Symbol, Multi-Timeframe (MSMTF) analysis.

Our framework fully supports the following configurations:

*   **Single Symbol, Single Timeframe**: The classic, focused view.
*   **Single Symbol, Multiple Timeframes (MTF)**: Analyze a single asset's trend and entry points across different time horizons.
*   **Multiple Symbols, Multiple Timeframes (MSMTF)**: Conduct sophisticated cross-market analysis, such as pairs trading or arbitrage, with perfectly synchronized data.
```python
import datetime
import json
import os
import signal
from time import sleep
from typing import Dict, List

import pandas as pd
import polars as pl
from loguru import logger

from aitrados_api import SubscribeEndpoint, ChartDataFormat
from aitrados_api import ClientConfig
from aitrados_api import DatasetClient
from aitrados_api import WebSocketClient
from aitrados_api import LatestOhlcMultiTimeframeManager
from aitrados_api import IntervalName

api_config = ClientConfig(
    secret_key=os.getenv("AITRADOS_SECRET_KEY", "YOUR_SECRET_KEY"),
    debug=True
)
api_client = DatasetClient(config=api_config)


def show_subscribe_handle_msg(client: WebSocketClient, message):
    print("subscriptions", json.dumps(client.all_subscribed_topics))


ws_client = WebSocketClient(
    secret_key=os.getenv("AITRADOS_SECRET_KEY", "YOUR_SECRET_KEY"),
    is_reconnect=True,
    show_subscribe_handle_msg=show_subscribe_handle_msg,
    endpoint=SubscribeEndpoint.REALTIME,
    debug=True
)


def multi_timeframe_callback(name, data: Dict[str, List[str | list | pl.DataFrame | pd.DataFrame]], **kwargs):
    print(f"==================Received data:{name}========================{datetime.datetime.now()}")

    for full_symbol, tf_data_list in data.items():
        for tf_data in tf_data_list:
            if isinstance(tf_data, list):
                print(json.dumps(tf_data[-2:], indent=2), "===len===", len(tf_data))
            else:
                print(tf_data)


latest_ohlc_multi_timeframe_manager = LatestOhlcMultiTimeframeManager(
    api_client=api_client,
    ws_client=ws_client,
    multi_timeframe_callback=multi_timeframe_callback,
    limit=150,  # data length limit
    works=10,
    data_format=ChartDataFormat.DICT  # multi_timeframe_callback return data format
)

is_close = False


def signal_handler(sig, frame):
    ws_client.close()
    global is_close
    is_close = True


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    ws_client.run(is_thread=True)

    # Add single symbol with single timeframe
    latest_ohlc_multi_timeframe_manager.add_item(
        item_data={
            "CRYPTO:GLOBAL:BTCUSD": [IntervalName.M60],
        },
        name="single_timeframe"
    )

    # Add single symbol with multiple timeframes
    latest_ohlc_multi_timeframe_manager.add_item(
        item_data={
            "CRYPTO:GLOBAL:BTCUSD": [IntervalName.M60, IntervalName.DAY],
        },
        name="multi_timeframe"
    )

    # Add multiple symbols with multiple timeframes
    latest_ohlc_multi_timeframe_manager.add_item(
        item_data={
            "CRYPTO:GLOBAL:BTCUSD": [IntervalName.M15, IntervalName.M60, IntervalName.DAY],
            "CRYPTO:GLOBAL:ETHUSD": [IntervalName.M15, IntervalName.M60, IntervalName.DAY]
        },
        name="multi_symbol_multi_timeframe"
    )

    # Add multiple stocks with multiple timeframes

    latest_ohlc_multi_timeframe_manager.add_item(
        item_data={
            "stock:us:tsla": [IntervalName.M5, IntervalName.M60, IntervalName.DAY],
            "stock:us:spy": [IntervalName.M5, IntervalName.M60, IntervalName.WEEK],
        },
        name="stock_multi_timeframe"
    )

    while not is_close:
        sleep(2)
    # Remove item example
    # latest_ohlc_multi_timeframe_manager.remove_item(name="multi_symbol_multi_timeframe")
    # latest_ohlc_multi_timeframe_manager.remove_item(name="multi_timeframe")
    # latest_ohlc_multi_timeframe_manager.remove_item(name="single_timeframe")
    # latest_ohlc_multi_timeframe_manager.remove_item(name="stock_multi_timeframe")
    logger.info("Exited")

```


## Authorization

This project requires a `Secret Key` provided by the Aitrados platform (for WebSocket API). Please visit [www.aitrados.com](https://www.aitrados.com/) to obtain your key(Currently free).

In the code examples, be sure to replace `YOUR_SECRET_KEY` with your own valid key.

## Contributing

We welcome contributions from the community! If you have any suggestions for improvements or find bugs, please feel free to participate in the following ways:
*   **Submit an Issue**: Report problems you encounter or suggest new features.
*   **Create a Pull Request**: If you've fixed a bug or implemented a new feature, we welcome your PR.

## License

This project is licensed under the [MIT](LICENSE) License.