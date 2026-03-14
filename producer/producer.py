from alpaca.data.live import StockDataStream
from alpaca.data.live import CryptoDataStream
from dotenv import load_dotenv
import os
from confluent_kafka import Producer
import json

load_dotenv()

class TradingProducer:

    def __init__(self):
        self.ALPACA_API_KEY = os.environ.get("ALPACA_API_KEY")
        self.ALPACA_SECRET_KEY = os.environ.get("ALPACA_SECRET_KEY")

        self.data_stream = CryptoDataStream(api_key = self.ALPACA_API_KEY, secret_key=self.ALPACA_SECRET_KEY)

        self.symbols = ["BTC/USD", "ETH/USD", "XRP/USD", "AVAX/USD", "LINK/USD"]

        self.kafka_producer = Producer({"bootstrap.servers" : os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")})


    async def trade_callback(self, trade):
        print("Trade Received: ", trade.symbol, trade.price, trade.size, trade.timestamp)
        print("-----------------------")

        kafka_val = json.dumps({"symbol": trade.symbol, "price": trade.price, "size": trade.size, "timestamp": str(trade.timestamp)}).encode("utf-8")

        self.kafka_producer.produce(topic="raw-ticks", value=kafka_val)
        self.kafka_producer.flush()



    def subscribe_trades(self):
        self.data_stream.subscribe_trades(self.trade_callback, *self.symbols)

    def start(self):
        self.data_stream.run()

    def stop(self):
        self.data_stream.stop()





if __name__ == "__main__":
    producer = TradingProducer()
    producer.subscribe_trades()
    producer.start()