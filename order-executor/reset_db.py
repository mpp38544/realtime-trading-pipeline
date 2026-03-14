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
    "TRUNCATE trades CASCADE;" \
    "TRUNCATE positions CASCADE;" \
    "TRUNCATE pnl CASCADE;"
)

connection.commit()

cursor.close()
connection.close()