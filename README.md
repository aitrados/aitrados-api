# aitrados-dataset-api

`aitrados-dataset-api` is the official Python client for the Aitrados data platform, **specifically designed for AI quantitative trading/training**.


We are committed to providing high-quality **training and trading data** for your AI strategies. The core advantage of this library is that it helps you easily integrate **naked K-line multi-timeframe technical analysis** with **real-time news and economic events** for fusion analysis, providing a solid data foundation for training complex AI models and executing time-critical real-time trading.

Github:https://github.com/aitrados/dataset-api

## Table of Contents

*   [Features](#features)
*   [Installation](#installation)
*   [Usage](#usage)
    *   [HTTP API - Get Historical Data](#http-api---get-historical-data)
    *   [WebSocket API - Subscribe to Real-time Data](#websocket-api---subscribe-to-real-time-data)
*   [Authorization](#authorization)
*   [Contributing](#contributing)
*   [License](#license)

## Features

*   **Designed for AI Fusion Analysis**: Seamlessly integrate naked K-line multi-timeframe technical analysis, real-time news events, and macroeconomic data to provide a unified data source for AI model training and real-time trading.
*   **Access Comprehensive Historical Financial Data via HTTP API:**
    *   OHLC (Open, High, Low, Close) data with multi-timeframe support
    *   Symbol information (stocks, cryptocurrencies, forex)
    *   Options chains and expiration dates
    *   Corporate actions (e.g., stock splits, dividends)
    *   Macroeconomic events and calendars
    *   Global trading holiday information
    *   Extensive historical financial news
*   **Subscribe to Real-time Data Streams via WebSocket API:**
    *   Real-time OHLC data (tick-by-tick or minute-level)
    *   Real-time news feeds
    *   Real-time economic event alerts

## Installation

You can install this library using pip:
```bash
pip install aitrados_api
```

## Usage

### HTTP API - Get Historical Data

You need to use your API key to initialize the `DatasetClient`.

```python
import os
from aitrados_api import SchemaAsset
from aitrados_api import ClientConfig, RateLimitConfig
from aitrados_api import  DatasetClient


config = ClientConfig(
    secret_key=os.getenv("AITRADOS_SECRET_KEY","YOUR_SECRET_KEY"),#Currently free
    debug=True
)

client=DatasetClient(config=config)
params = {
    "schema_asset": SchemaAsset.CRYPTO,
    "country_symbol": "GLOBAL:BTCUSD",
    "interval": "1m",
    "from_date": "2025-07-18 00:00:00",
    "to_date": "2025-09-05 23:59:59",
    "format": "json",
    "limit": 30
}
#***************************************OHLC DATA***************************#
'''
## Get historical OHLC data
for ohlc in client.ohlc.ohlcs(**params):
    print(ohlc)
'''


# Get latest OHLC data.use for real-time data
ohlc_latest=client.ohlc.ohlcs_latest(**params)
print(ohlc_latest)


#***************************************symbol reference***************************#
'''
stock_reference=client.reference.reference(schema_asset=SchemaAsset.STOCK,country_symbol="US:TSLA")
crypto_reference=client.reference.reference(schema_asset=SchemaAsset.CRYPTO,country_symbol="GLOBAL:BTCUSD")
forex_reference=client.reference.reference(schema_asset=SchemaAsset.FOREX,country_symbol="GLOBAL:EURUSD")
'''




#***************************************OPTIONS INFORMATION***************************#
'''
# Get options information
for options in client.reference.search_option(schema_asset=SchemaAsset.STOCK,country_symbol="US:spy",option_type="call",moneyness="in_the_money",ref_asset_price=450.50,limit=100):
    print(options)
'''
'''
# Get options expiration date list
expiration_date_list= client.reference.options_expiration_date_list(schema_asset=SchemaAsset.STOCK, country_symbol="US:SPY", limit=100, format="json")
'''

#***************************************stock corporate action***************************#
'''
# Get stock corporate action list
for actions in client.reference.stock_corporate_action_list(country_symbol="US:spy",from_date="2020-08-18",action_type="split",limit=100):
    print(actions)
'''
#***************************************economic event***************************#
'''
# Get economic event codes of all countries
event_codes= client.economic.event_codes()
'''

'''
# Get economic event list
event_list= client.economic.event_list(country_iso_code="US")
'''

'''
# Get economic event by date
event= client.economic.event()
'''



#***************************************holiday***************************#
'''
# Get holiday list
for holiday_list in client.holiday.holiday_list(full_symbol="stock:US:*",from_date="2023-01-01",to_date="2026-12-31",limit=100):
    print(holiday_list)
'''

'''
# Get holiday codes of all countries
holiday_codes= client.holiday.holiday_codes()
'''

#***************************************news***************************#

'''
# Get news list
for news_list in client.news.news_list(full_symbol="stock:US:TSLA",from_date="2025-07-01",to_date="2025-12-31",limit=100):
    print(news_list)
'''

'''
# Get latest news.use for real-time data
news_latest= client.news.news_latest(full_symbol="stock:US:TSLA",limit=5)
'''
```


### WebSocket API - Subscribe to Real-time Data

With the `WebSocketClient`, you can subscribe to various real-time data streams.

```python
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
    logger.info(f"✅ Subscription status: {message}")

    print("subscriptions",client.all_subscribed_topics)


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
    debug=False
)


def signal_handler(sig, frame):
    client.close()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    client.run(is_thread=False)
    """
    while True:
        sleep(2)
    """
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