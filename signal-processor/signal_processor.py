import numpy as np
from confluent_kafka import Consumer
from confluent_kafka import Producer
import json
from datetime import datetime, timezone
import os

class KalmanFilter:
    def __init__(self):
        self.F = np.array([[1, 1],
                           [0, 1]])
        
        self.H = np.array([[1, 0]])

        self.Q = np.array([[1e-4, 0],
                           [0, 1e-4]])
        
        self.R = np.array([[0.1]])

        self.P =  np.eye(2)

        self.x  = np.array([[0.0], 
                            [0.0]])

        self.I = np.eye(2)

    def update(self, obs):
        self.x = self.F @ self.x

        self.P = self.F @ self.P @ self.F.T + self.Q

        self.K = self.P @ self.H.T @ np.linalg.inv(self.H @ self.P @ self.H.T + self.R)

        self.x = self.x + self.K @ (obs - self.H @ self.x)

        self.P = (self.I - self.K @ self.H) @ self.P

        return self.x

class AvellanedaStoikov:
    def __init__(self):
        self.gamma = 0.1
        self.kappa = 1.5
        self.max_pos = 0.01
        self.order_size = 0.001

    def calculate_quotes(self, fair_price, sigma, inv, t_left):

        sigma_sq = sigma ** 2
        inv_skew = inv * self.gamma * sigma_sq * t_left

        inv_skew = np.clip(inv_skew, -fair_price * 0.01, fair_price * 0.01)

        reserv_price = fair_price - inv_skew

        spread = (self.gamma * sigma_sq * t_left) + (2/self.gamma) * np.log(1 + self.gamma / self.kappa)

        spread = np.clip(spread, fair_price * 0.0002, np.inf)

        bid = reserv_price - spread / 2

        ask = reserv_price + spread / 2

        return [bid, ask]

class SignalProcessor:
    def __init__(self):
        self.kF = {}
        self.aS = {}
        
        self.kafka_consumer = Consumer({"bootstrap.servers": os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"), "group.id": "signal-processor", "auto.offset.reset": "latest"})

        self.kafka_consumer.subscribe(["raw-ticks"])

        self.kafka_producer = Producer({"bootstrap.servers": os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")})

        self.inv = {}

        self.decay = 0.94

        self.lastPrice = {}
        self.currentVol = {}

    def calc_vol(self, symbol, price):
        if self.lastPrice[symbol] <= 0.0:
            self.lastPrice[symbol] = price
            return np.sqrt(self.currentVol[symbol])
        
        logReturn = np.log(price / self.lastPrice[symbol])

        self.currentVol[symbol] = (self.decay * self.currentVol[symbol]) + ((1.0 - self.decay) * (logReturn ** 2))

        self.lastPrice[symbol] = price

        return np.sqrt(self.currentVol[symbol])

    def process_tick(self, tick):
        '''{
        "symbol": trade.symbol, 
        "price": trade.price, 
        "size": trade.size, 
        "timestamp": str(trade.timestamp)
        }'''

        symbol = tick["symbol"]
        price = tick["price"]
        timestamp = tick["timestamp"]

        if symbol not in self.kF:
            self.kF[symbol] = KalmanFilter()
            self.aS[symbol] = AvellanedaStoikov()

            self.inv[symbol] = 0.0
            self.lastPrice[symbol] = 0.0
            self.currentVol[symbol] = 1e-4

        size = self.aS[symbol].order_size

        if self.kF[symbol].x[0][0] == 0.0:
            self.kF[symbol].x = np.array([[price], [0.0]])

        obs = np.array([[price]])

        state = self.kF[symbol].update(obs)

        fair_price = float(state[0][0])

        sigma = self.calc_vol(symbol, fair_price)

        midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

        t_left = 1 - (datetime.now(timezone.utc) - midnight).total_seconds() / 86400

        bid, ask = self.aS[symbol].calculate_quotes(fair_price, sigma, self.inv[symbol], t_left)
        
        bid = float(bid)
        ask = float(ask)

        signals = []

        print(f"Signal: {symbol} @ {price} | fair: {fair_price:.4f} | bid: {bid:.4f} | ask: {ask:.4f}")

        latency = datetime.now(timezone.utc) - datetime.fromisoformat(timestamp)
        print(f"Processing latency: {latency.total_seconds()*1000:.2f}ms")
        print("-----------------------")

        if price <= bid and self.inv[symbol] < self.aS[symbol].max_pos:
            trade_sig = {"symbol": symbol, "side": "BUY", "price": price, "val": bid, "fair_price": fair_price, "size": size, "inventory": self.inv[symbol], "timestamp" : timestamp}

            signals.append(trade_sig)

        if price >= ask and self.inv[symbol] > -self.aS[symbol].max_pos:
            trade_sig = {"symbol": symbol, "side": "SELL", "price": price, "val": ask, "fair_price": fair_price, "size": size, "inventory": self.inv[symbol], "timestamp" : timestamp}

            signals.append(trade_sig)

        for sig in signals:
            self.kafka_producer.produce(topic="trading-signals", value=json.dumps(sig).encode("utf-8"))
        
        self.kafka_producer.flush()

    def run(self):
        while True:
            msg = self.kafka_consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                print(f"Consumer error: {msg.error()}")
                print("-----------------------")
                continue

            try:
                tick = json.loads(msg.value().decode("utf-8"))
                print("-----------------------")
                self.process_tick(tick)

            except Exception as e:
                print(f"Error processing tick: {e}")
                continue

if __name__ == "__main__":
    processor = SignalProcessor()
    processor.run()



