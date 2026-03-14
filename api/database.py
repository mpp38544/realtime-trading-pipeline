import psycopg2
import os

def dbconn():
    connection = psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=int(os.environ.get("POSTGRES_PORT", "5433")),
        database="tradingdb",
        user="trader",
        password="trader123"
    )

    return connection