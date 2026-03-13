from confluent_kafka import Consumer
import psycopg2
import json

class OrderExecutor:
    def __init__(self):
        self.kafka_consumer = Consumer({"bootstrap.servers" : "localhost:9092", "group.id": "order-executor", "auto.offset.reset": "latest"})

        self.kafka_consumer.subscribe(["trading-signals"])

        self.conn = psycopg2.connect(
            host="localhost",
            port=5433,
            database="tradingdb",
            user="trader",
            password="trader123"
        )

        self.cursor = self.conn.cursor()

        self.inv = {}
        self.cash_bal = {}

        self.realised_pnl = {}
        self.unrealised_pnl = {}

        self.portfolio_pnl = 0

    
    def execute_signal(self, sig):

        side = sig["side"]
        price = sig["price"]
        val = sig["val"]
        symbol = sig["symbol"]
        size = sig["size"]
        timestamp = sig["timestamp"]

        if symbol not in self.inv:
            self.inv[symbol] = 0.0
            self.cash_bal[symbol] = 10000.0
            self.realised_pnl[symbol] = 0.0
            self.unrealised_pnl[symbol] = 0.0

        if side == "BUY":
            self.inv[symbol] += size
            self.cash_bal[symbol] -= (val * size)
            
        elif side == "SELL":
            self.inv[symbol] -= size
            self.cash_bal[symbol] += (val * size)
    
        self.unrealised_pnl[symbol] = self.inv[symbol] * price
        self.realised_pnl[symbol] = self.cash_bal[symbol]

        self.portfolio_pnl = sum(self.inv[s] * price + self.cash_bal[s] for s in self.inv)

        self.write_trade(symbol, side, price, size, timestamp)
        self.write_position(symbol, self.inv[symbol], self.cash_bal[symbol], timestamp)
        self.write_pnl(symbol, self.unrealised_pnl[symbol], self.realised_pnl[symbol], self.realised_pnl[symbol] + self.unrealised_pnl[symbol], self.portfolio_pnl, timestamp)

        self.conn.commit()

        print(f"{side} {symbol} @ {val:.2f} | inv: {self.inv[symbol]:.4f} | cash: {self.cash_bal[symbol]:.2f} | portfolio PnL: {self.portfolio_pnl:.2f}")

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

    def run(self):
        while True:
            msg = self.kafka_consumer.poll(1.0)

            if msg is None:
                continue

            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue

            try:
                signal = json.loads(msg.value().decode("utf-8"))
                self.execute_signal(signal)

            except Exception as e:
                print(f"Error processing tick: {e}")
                continue
    

if __name__ == "__main__":
    order_executor = OrderExecutor()
    order_executor.run()