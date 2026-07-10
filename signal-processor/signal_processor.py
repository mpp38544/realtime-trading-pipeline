import numpy as np
from confluent_kafka import Consumer
from confluent_kafka import Producer
import json
from datetime import datetime, timezone
import os
import psycopg2
import sys
from prometheus_client import Counter, Gauge, start_http_server

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
        self.gamma = 0.3
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
    ticks_processed = Counter('ticks_processed_total', 'Total ticks processed')

    signals_generated = Counter('signals_generated_total', 'Total signals generated')

    processing_latency = Gauge('processing_latency_ms', 'Processing Latency (ms)')

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

        self.conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", "5433")),
            database="tradingdb",
            user="trader",
            password="trader123"
        )
        
        self.cursor = self.conn.cursor()

        self.ensure_schema()

        self.load_state()


        start_http_server(8002)

    def load_state(self):
        self.cursor.execute(
            "SELECT symbol, inventory FROM state"
        )
        rows = self.cursor.fetchall()
        
        if not rows:
            print("No saved state — starting fresh")
            return
        
        for row in rows:
            symbol = row[0]
            if symbol not in self.inv:
                self.kF[symbol] = KalmanFilter()
                self.aS[symbol] = AvellanedaStoikov()
                self.lastPrice[symbol] = 0.0
                self.currentVol[symbol] = 1e-4
            self.inv[symbol] = row[1]
        
        print(f"Loaded inventory for {len(rows)} symbols")

    def ensure_schema(self):
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS trades ("
            "id SERIAL PRIMARY KEY,"
            "symbol VARCHAR(20),"
            "side VARCHAR(20),"
            "price FLOAT,"
            "quantity FLOAT,"
            "timestamp TIMESTAMPTZ)"
        )

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS positions ("
            "id SERIAL PRIMARY KEY,"
            "symbol VARCHAR(20),"
            "inventory FLOAT,"
            "cash_balance FLOAT,"
            "timestamp TIMESTAMPTZ)"
        )

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS pnl ("
            "id SERIAL PRIMARY KEY,"
            "symbol VARCHAR(20),"
            "unrealised FLOAT,"
            "realised FLOAT,"
            "total FLOAT,"
            "portfolio_pnl FLOAT,"
            "timestamp TIMESTAMPTZ)"
        )

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS logs ("
            "id SERIAL PRIMARY KEY,"
            "service VARCHAR(20),"
            "message TEXT,"
            "timestamp TIMESTAMPTZ)"
        )

        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS state ("
            "id SERIAL PRIMARY KEY,"
            "symbol VARCHAR(20) UNIQUE,"
            "inventory FLOAT,"
            "cash_balance FLOAT,"
            "unrealised FLOAT,"
            "realised FLOAT,"
            "portfolio_pnl FLOAT,"
            "timestamp TIMESTAMPTZ)"
        )

        self.conn.commit()

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

        self.processing_latency.set(latency.total_seconds() * 1000)
        self.ticks_processed.inc()

        print(f"Processing latency: {latency.total_seconds()*1000:.2f}ms")
        print("-----------------------")

        #BUY
        if price <= bid and self.inv[symbol] < self.aS[symbol].max_pos:
            trade_sig = {"symbol": symbol, "side": "BUY", "price": price, "val": bid, "fair_price": fair_price, "size": size, "inventory": self.inv[symbol], "timestamp" : timestamp}

            self.write_log(symbol, "BUY", bid, size)

            signals.append(trade_sig)

        elif self.inv[symbol] < -self.aS[symbol].max_pos * 0.8:
            rebalance_size = abs(self.inv[symbol])
            trade_sig = {"symbol": symbol, "side": "BUY", "price": price, "val": price, "fair_price": fair_price, "size": rebalance_size, "inventory": self.inv[symbol], "timestamp": timestamp}
            signals.append(trade_sig)

        #SELL
        if price >= ask and self.inv[symbol] > -self.aS[symbol].max_pos:
            trade_sig = {"symbol": symbol, "side": "SELL", "price": price, "val": ask, "fair_price": fair_price, "size": size, "inventory": self.inv[symbol], "timestamp" : timestamp}

            self.write_log(symbol, "SELL", ask, size)

            signals.append(trade_sig)

        elif self.inv[symbol] > self.aS[symbol].max_pos * 0.8:
            rebalance_size = abs(self.inv[symbol])
            trade_sig = {"symbol": symbol, "side": "SELL", "price": price, "val": price, "fair_price": fair_price, "size": rebalance_size, "inventory": self.inv[symbol], "timestamp": timestamp}
            signals.append(trade_sig)
        
        for sig in signals:
            self.kafka_producer.produce(topic="trading-signals", value=json.dumps(sig).encode("utf-8"))
            self.signals_generated.inc()
        
        self.kafka_producer.flush()

    def write_log(self, symbol, side, quote, qty):
        self.cursor.execute(
            "INSERT INTO logs (service, message, timestamp) VALUES (%s, %s, %s)",
            ("processor", f"Submitted {side} order: {symbol} @ ${quote}, Qty: {qty}", datetime.now(timezone.utc))
        )

        self.conn.commit()

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



