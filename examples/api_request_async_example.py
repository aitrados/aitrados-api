import asyncio
import os

from aitrados_api import *


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
    rename_column_name_mapping = {"interval": "timeframe", }
    filter_column_names = ["datetime", "timeframe", "open", "high", "low", "close", "volume"]
    to_format = ApiListResultToFormatData(ohlc_latest, rename_column_name_mapping=rename_column_name_mapping,
                                          filter_column_names=filter_column_names, limit=None)
    pl_df = to_format.get_polars()
    pd_df = to_format.get_pandas()
    csv_string = to_format.get_csv()
    data_list = to_format.get_list()
    pass

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