
import os
import time

from aitrados_api.common_lib.common import load_env_file
from aitrados_api.common_lib.contant import SubscribeEndpoint, SchemaAsset, IntervalName
from aitrados_api.common_lib.subscribe_api.websocks_client import WebSocketClient
from aitrados_api.universal_interface.callback_manage import CallbackManage
from aitrados_api.universal_interface.aitrados_instance import *
from aitrados_api.universal_interface.trade_middleware_instance import AitradosTradeMiddlewareInstance

#os.environ["DEBUG"]="true"
#os.environ["AITRADOS_SECRET_KEY"]="YOUR_SECRET_KEY"
load_env_file(file=None, override=True)
"""
aitrados middleware features
1. Solves communication between modules, processes, and programs. Enables functional decoupling of complex trading systems. For example: llm-->quantitative strategy-->llm-->emotion management-->capital management-->llm complex circular calculation strategy
2. API data reuse. API data is shared with other modules. For example, ohlc data is simultaneously provided to both llm mcp and traditional quantitative strategies
3. Easy implementation of complex trading systems:
    OHLC Data Processing
    Macroeconomic Analysis
    Fundamental Analysis
    Traditional Technical Indicators
    Advanced Price Action Strategies
    News & Event Processing
    Breaking News Analysis
    Financial Calendar Events
    Risk Management
    Financial MCP Tools
    LLM-Powered Strategies
4. Solves Python's global lock performance issue
6. One-click management of api_client, ws_client, latest_symbol_charting_manager, latest_ohlc_multi_timeframe_manager. You can also configure them individually
5. Multi-language collaboration https://zeromq.org/get-started/?language=rust#

"""

'''
## Modify aitrados config
from aitrados_api.universal_interface.aitrados_instance import api_client_instance,ws_client_instance,latest_ohlc_multi_timeframe_manager_instance
ws_client_instance.endpoint=SubscribeEndpoint.REALTIME
'''

'''
## If you are in the same process, you can still use traditional subscription callbacks
def on_custom_handle_msg(_ws_client:WebSocketClient,msg,*args,**kwargs):
    print("on_custom_handle_msg",msg)
CallbackManage.add_custom_handle_msg(on_custom_handle_msg)
'''

'''
## You can still use traditional methods to get data and subscribe:
Instantiated class objects from aitrados_api.universal_interface.aitrados_instance import *
api_request_async_example.py
api_request_example.py,
websocket_subscription_example.py
latest_ohlc_multi_timeframe_alignment_example.py
latest_ohlc_chart_roll_flow_example.py
## If not in the same process, new instances will be created
'''

if __name__ == "__main__":
    AitradosTradeMiddlewareInstance.run_all()
    try:
        # Keep the main thread running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("closing...")