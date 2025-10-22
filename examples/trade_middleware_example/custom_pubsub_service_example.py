import threading
import time

from aitrados_api.trade_middleware.publisher import async_publisher_instance
"""
at first ,run "python run_trade_middleware_example.py"
"""


test_sub_topic="on_my_first_sub_topic"
def publish_service_example():
    i = 0

    while True:

        msg = f"Hello {i} {time.time()}".encode()
        async_publisher_instance.send_topic(test_sub_topic,msg)
        i += 1
        time.sleep(2)

def subscriber_client_example():
    from aitrados_api.trade_middleware.subscriber import AsyncSubscriber
    class MyAsyncSubscriber(AsyncSubscriber):
        """
        Asynchronous function callback
        """

        async def on_my_first_sub_topic(self, msg):
            # my_first_sub_topic is from custom_pub_service_example.py
            print(test_sub_topic, msg)
            pass

    subscriber = MyAsyncSubscriber()
    subscriber.run()
    subscriber.subscribe_topics(test_sub_topic)

if __name__ == "__main__":
    threading.Thread(target=publish_service_example, daemon=True).start()

    subscriber_client_example()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("close...")


