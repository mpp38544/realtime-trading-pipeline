from confluent_kafka import Consumer
import psycopg2
import json
import os
from datetime import datetime, timezone
from prometheus_client import Counter, Gauge, start_http_server

class OrderExecutor:
    orders_executed = Counter('orders_executed_total', 'Total orders executed')

    portfolio_pnl_gauge = Gauge('portfolio_pnl_gauge', 'Portfolio PnL')

    def __init__(self):
        self.kafka_consumer = Consumer({"bootstrap.servers": os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"), "group.id": "order-executor", "auto.offset.reset": "latest"})

        self.kafka_consumer.subscribe(["trading-signals"])

        self.conn = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST", "localhost"),
            port=int(os.environ.get("POSTGRES_PORT", "5433")),
            database="tradingdb",
            user="trader",
            password="trader123"
        )

        self.inv = {}
        self.cash_bal = {}

        self.realised_pnl = {}
        self.unrealised_pnl = {}

        self.starting_cash = 10000.0
        self.portfolio_pnl = 0

        self.cursor = self.conn.cursor()
        self.load_state()
        start_http_server(8003)

    def load_state(self):
        self.cursor.execute(
            "SELECT symbol, inventory, cash_balance, realised, unrealised, portfolio_pnl FROM state"
        )

        rows = self.cursor.fetchall()

        if not rows: 
            return
        
        for row in rows:
            symbol = row[0]
            self.inv[symbol] = row[1]
            self.cash_bal[symbol] = row[2]
            self.realised_pnl[symbol] = row[3]
            self.unrealised_pnl[symbol] = row[4]
            self.portfolio_pnl = row[5]

        print(f"Loaded state for {len(rows)} symbols")
    
    def execute_signal(self, sig):

        side = sig["side"]
        price = sig["price"]
        val = sig["val"]
        symbol = sig["symbol"]
        size = sig["size"]
        timestamp = sig["timestamp"]

        if symbol not in self.inv:
            self.inv[symbol] = 0.0
            self.cash_bal[symbol] = 0.0
            self.realised_pnl[symbol] = 0.0
            self.unrealised_pnl[symbol] = 0.0

        if side == "BUY":
            self.inv[symbol] += size
            self.cash_bal[symbol] -= (val * size)
            
        elif side == "SELL":
            self.inv[symbol] -= size
            self.cash_bal[symbol] += (val * size)
    
        self.unrealised_pnl[symbol] = self.cash_bal[symbol] + self.inv[symbol] * price
        
        if abs(self.inv[symbol]) < 1e-9:
            self.realised_pnl[symbol] += self.cash_bal[symbol]
            self.cash_bal[symbol] = 0.0
            self.inv[symbol] = 0.0


        self.portfolio_pnl = sum(self.unrealised_pnl[s] + self.realised_pnl[s] for s in self.inv)

        self.portfolio_pnl_gauge.set(self.portfolio_pnl)

        self.write_trade(symbol, side, price, size, timestamp)
        self.write_position(symbol, self.inv[symbol], self.cash_bal[symbol], timestamp)
        self.write_pnl(symbol, self.unrealised_pnl[symbol], self.realised_pnl[symbol], self.realised_pnl[symbol] + self.unrealised_pnl[symbol], self.portfolio_pnl, timestamp)
        self.write_log(side, symbol, val, size)
        self.orders_executed.inc()
        self.write_state(symbol, self.inv[symbol], self.cash_bal[symbol], self.realised_pnl[symbol], self.unrealised_pnl[symbol], self.portfolio_pnl)

        self.conn.commit()

        print(f"{side} {symbol} @ {val:.2f} | inv: {self.inv[symbol]:.4f} | cash: {self.cash_bal[symbol]:.2f} | portfolio PnL: {self.portfolio_pnl:.2f}")
        print("-----------------------")

    def write_trade(self, symbol, side, price, quantity, timestamp):
        self.cursor.execute(
            "INSERT INTO trades (symbol, side, price, quantity, timestamp) VALUES (%s, %s, %s, %s, %s)",

            (symbol, side, price, quantity, timestamp)
        )

    def write_position(self, symbol, inventory, cash_balance, timestamp):
        self.cursor.execute(
            "INSERT INTO positions (symbol, inventory, cash_balance, timestamp) VALUES (%s, %s, %s, %s)",
            (symbol, inventory, cash_balance, timestamp)
        )

    def write_pnl(self, symbol, unrealised, realised, total, portfolio_pnl, timestamp):
        self.cursor.execute(
            "INSERT INTO pnl (symbol, unrealised, realised, total, portfolio_pnl, timestamp) VALUES (%s, %s, %s, %s, %s, %s)",

            (symbol, unrealised, realised, total, portfolio_pnl, timestamp)
        )
    
    def write_log(self, side, symbol, quote, qty):
        self.cursor.execute(
            "INSERT INTO logs (service, message, timestamp) VALUES (%s, %s, %s)",
            ("executor", f"Executed {side} order: {symbol} @ ${quote}, Qty: {qty}", datetime.now(timezone.utc))
        )

    def write_state(self, symbol, inventory, cash_bal, realised, unrealised, portfolio):
        self.cursor.execute("""
            INSERT INTO state (symbol, inventory, cash_balance, realised, unrealised, portfolio_pnl, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (symbol) DO UPDATE set
                inventory = EXCLUDED.inventory,
                cash_balance = EXCLUDED.cash_balance,
                realised = EXCLUDED.realised,
                unrealised = EXCLUDED.unrealised,
                portfolio_pnl = EXCLUDED.portfolio_pnl,
                timestamp = EXCLUDED.timestamp""",
            (symbol, inventory, cash_bal, realised, unrealised, portfolio, datetime.now(timezone.utc))
        )

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
                signal = json.loads(msg.value().decode("utf-8"))
                self.execute_signal(signal)

            except Exception as e:
                print(f"Error processing tick: {e}")
                print("-----------------------")
                continue
    

if __name__ == "__main__":
    order_executor = OrderExecutor()
    order_executor.run()