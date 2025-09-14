


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