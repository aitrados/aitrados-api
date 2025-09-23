


class SubscribeEndpoint:
    REALTIME = "wss://realtime.dataset-sub.aitrados.com"
    DELAYED = "wss://delayed.dataset-sub.aitrados.com"

class ApiEndpoint:
    DEFAULT = "https://default.dataset-api.aitrados.com"
class SchemaAsset:
    STOCK = "stock"
    FUTURE = "future"
    CRYPTO = "crypto"
    FOREX = "forex"
    OPTION="option"


    @classmethod
    def get_array(cls):
        return [
            cls.STOCK,
            cls.FUTURE,
            cls.CRYPTO,
            cls.FOREX,
            cls.OPTION
        ]
class EcoEventPreviewIntervalName:
    DAY30 = "30DAY"
    WEEK2 = "2WEEK"
    WEEK1 = "1WEEK"
    DAY1 = "1DAY"
    M60 = "60M"
    M15 = "15M"
    M5 = "5M"
    REALTIME= "REALTIME"
    def get_non_realtime_array(cls):
        return [
            cls.DAY30,
            cls.WEEK2,
            cls.WEEK1,
            cls.DAY1,
            cls.M60,
            cls.M15,
            cls.M5
        ]
class IntervalName:
    MON="MON"
    WEEK="WEEK"
    DAY="DAY"
    M240="240M"
    M120="120M"
    M60="60M"
    M30="30M"
    M15="15M"
    M10="10M"
    M5="5M"
    M3="3M"
    M1="1M"
    @classmethod
    def get_array(cls):
        return [
            cls.MON,
            cls.WEEK,
            cls.DAY,
            cls.M240,
            cls.M120,
            cls.M60,
            cls.M30,
            cls.M15,
            cls.M10,
            cls.M5,
            cls.M3,
            cls.M1
        ]
    @classmethod
    def get_non_intraday_array(cls):
        return [
            cls.MON,
            cls.WEEK,
            cls.DAY,
            ]
    @classmethod
    def get_index(cls, interval):
        return cls.get_array().index(interval)
    @classmethod
    def is_in_array(cls, interval):
        return interval in cls.get_array()
    @classmethod
    def get_interval(cls, index):
        if index < 0 or index >= len(cls.get_array()):
            raise ValueError("Index out of range")
        return cls.get_array()[index]
class ApiDataFormat:
    JSON="json"
    CSV="csv"
class ChartDataFormat:
    DICT="dict"
    CSV="csv"
    PANDAS="pandas"
    POLARS="polars"
    @classmethod
    def get_array(cls):
        return [
            cls.DICT,
            cls.CSV,
            cls.PANDAS,
            cls.POLARS
        ]