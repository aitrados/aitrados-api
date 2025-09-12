


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