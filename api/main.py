from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import database
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/trades")
def get_trades():
    conn = database.dbconn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM trades ORDER BY timestamp DESC LIMIT 8"
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
        "SELECT * FROM pnl WHERE timestamp > NOW() - INTERVAL '1000 hours' ORDER BY timestamp ASC"
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
        "SELECT realised, unrealised, portfolio_pnl, timestamp FROM pnl ORDER BY timestamp DESC LIMIT 1"
    )

    row = cursor.fetchone()
    cursor.close()
    conn.close()

    if row is None:
        return {"realised": 0, "unrealised": 0, "portfolio_pnl": 0, "timestamp": None}

    cols = ["realised", "unrealised", "portfolio_pnl", "timestamp"]
    return dict(zip(cols, row))


@app.get("/health")
def get_health():
    return {"status": "ok"}


@app.get("/metrics")
def get_metrics():
    conn = database.dbconn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT portfolio_pnl, timestamp FROM pnl ORDER BY timestamp ASC"
    )

    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    pnl_vals =  np.array([row[0] for row in rows])

    if len(pnl_vals) < 2:
        cursor.close()
        conn.close()
        return {"sharpe_ratio": None, 
                "max_drawdown": None}

    returns = np.diff(pnl_vals)

    timestamps = [row[1] for row in rows]
    if len(timestamps) > 1:
        avg_seconds = (timestamps[-1] - timestamps[0]).total_seconds() / len(timestamps)
        periods_per_year = 365 * 24 * 3600 / avg_seconds
    else:
        periods_per_year = 525600

    sharpe = np.mean(returns) / np.std(returns) * np.sqrt(periods_per_year)


    peak = np.maximum.accumulate(pnl_vals)
    drawdown = (peak - pnl_vals) / peak

    max_drawdown = float(np.max(drawdown))


    cursor.close()
    conn.close()
    return {"sharpe_ratio": round(float(sharpe), 4),
            "max_drawdown" : max_drawdown}


@app.get("/drawdown")
def get_drawdown():
    conn = database.dbconn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT portfolio_pnl, timestamp FROM pnl ORDER BY timestamp ASC"
    )

    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    pnl_vals =  np.array([row[0] for row in rows])

    timestamps = [row[1] for row in rows]

    peak = np.maximum.accumulate(pnl_vals)
    drawdown = (peak - pnl_vals) / peak
    
    cursor.close()
    conn.close()
    return [{"timestamp": str(timestamps[i]),
             "drawdown": float(drawdown[i])} for i in range(len(drawdown))]

@app.get("/logs")
def get_logs():
    conn = database.dbconn()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM logs ORDER BY timestamp DESC LIMIT 20"
    )

    cols = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()

    res =  [dict(zip(cols, row)) for row in rows]

    cursor.close()
    conn.close()
    return res