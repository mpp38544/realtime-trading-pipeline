import psycopg2

print("Connecting...")
connection = psycopg2.connect(
    host="localhost",
    port=5433,
    database="tradingdb",
    user="trader",
    password="trader123"
)
print("Connected")

cursor = connection.cursor()
cursor.execute("TRUNCATE TABLE trades, positions, pnl, logs, state CASCADE")
connection.commit()
print("Done")

cursor.close()
connection.close()