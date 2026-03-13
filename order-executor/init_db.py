import psycopg2

connection = psycopg2.connect(
    host="localhost",
    port=5433,
    database="tradingdb",
    user="trader",
    password="trader123"
)

cursor = connection.cursor()

cursor.execute(
    "CREATE TABLE IF NOT EXISTS trades (" \
    "id SERIAL PRIMARY KEY," \
    "symbol VARCHAR(20)," \
    "side VARCHAR(20)," \
    "price FLOAT," \
    "quantity FLOAT," \
    "timestamp TIMESTAMPTZ)"
)

cursor.execute(
    "CREATE TABLE IF NOT EXISTS positions (" \
    "id SERIAL PRIMARY KEY," \
    "symbol VARCHAR(20)," \
    "inventory FLOAT," \
    "cash_balance FLOAT," \
    "timestamp TIMESTAMPTZ)"
)

cursor.execute(
    "CREATE TABLE IF NOT EXISTS pnl (" \
    "id SERIAL PRIMARY KEY," \
    "symbol VARCHAR(20)," \
    "unrealised FLOAT," \
    "realised FLOAT," \
    "total FLOAT," \
    "portfolio_pnl FLOAT," \
    "timestamp TIMESTAMPTZ)"
)

connection.commit()

cursor.close()
connection.close()