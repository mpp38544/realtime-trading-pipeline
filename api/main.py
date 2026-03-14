from fastapi import FastAPI
import database

app = FastAPI()

@app.get("/trades")
def get_trades():
    conn = database.dbconn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 50"
    )

    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    res =  [dict(zip(cols, row)) for row in rows]

    cursor.close()
    conn.close()
    return res



@app.get("/positions")
def get_positions():
    conn = database.dbconn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT DISTINCT ON (symbol) symbol, inventory, cash_balance, timestamp " \
        "FROM positions " \
        "ORDER BY symbol, timestamp DESC"
    )

    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    res =  [dict(zip(cols, row)) for row in rows]

    cursor.close()
    conn.close()
    return res



@app.get("/pnl")
def get_pnl():
    conn = database.dbconn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * from pnl ORDER BY timestamp DESC LIMIT 100"
    )

    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    res =  [dict(zip(cols, row)) for row in rows]

    cursor.close()
    conn.close()
    return res

@app.get("/portfolio")
def get_portfolio():
    conn = database.dbconn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT portfolio_pnl, timestamp FROM pnl ORDER BY timestamp DESC LIMIT 1"
    )

    cols = [desc[0] for desc in cursor.description]
    row = cursor.fetchone()

    res =  dict(zip(cols, row))

    cursor.close()
    conn.close()
    return res


@app.get("/health")
def get_health():
    return {"status": "ok"}