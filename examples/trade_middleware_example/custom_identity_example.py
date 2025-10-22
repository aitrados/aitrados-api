from aitrados_api.trade_middleware.identity_mixin import *
class RpcFunction(RpcFunctionMixin):
    LAST_OHLC_PRICE_ROW = "last_ohlc_price_row"
    FIRST_OHLC_PRICE_ROW = "first_ohlc_price_row"
class Channel(ChannelMixin):
    MY_TEST_SUB = b"my_test_sub"
    MY_SECOND_SUB = b"my_second_sub"
class Identity(IdentityMixin):
    backend_identity = "my_first_package"
    fun = RpcFunction
    channel = Channel
my_custom_identity_example=Identity

