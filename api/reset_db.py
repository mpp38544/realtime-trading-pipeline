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
print("Truncating trades...")
cursor.execute("TRUNCATE TABLE trades CASCADE")
print("Truncating positions...")
cursor.execute("TRUNCATE TABLE positions CASCADE")
print("Truncating pnl...")
cursor.execute("TRUNCATE TABLE pnl CASCADE")
print("Truncating logs...")
cursor.execute("TRUNCATE TABLE logs CASCADE")
print("Truncating state...")
cursor.execute("TRUNCATE TABLE state CASCADE")
print("Committing...")
connection.commit()
print("Done")

cursor.close()
connection.close()