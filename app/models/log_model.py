import sqlite3
import os

def get_db(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = get_db(db_path)
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS logs (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT NOT NULL,
            ip        TEXT NOT NULL,
            status    TEXT NOT NULL,   -- SUCCESS / FAILED
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            ip        TEXT NOT NULL,
            severity  TEXT NOT NULL,   -- LOW / MEDIUM / HIGH / CRITICAL
            count     INTEGER NOT NULL,
            message   TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    conn.commit()
    conn.close()

# ── Log queries ──────────────────────────────────────────────────────────────

def insert_log(db_path, username, ip, status):
    conn = get_db(db_path)
    conn.execute(
        "INSERT INTO logs (username, ip, status) VALUES (?, ?, ?)",
        (username, ip, status)
    )
    conn.commit()
    conn.close()

def get_all_logs(db_path, limit=200):
    conn = get_db(db_path)
    rows = conn.execute(
        "SELECT * FROM logs ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_stats(db_path):
    conn = get_db(db_path)
    total   = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    failed  = conn.execute("SELECT COUNT(*) FROM logs WHERE status='FAILED'").fetchone()[0]
    success = conn.execute("SELECT COUNT(*) FROM logs WHERE status='SUCCESS'").fetchone()[0]
    alerts  = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
    conn.close()
    return {"total": total, "failed": failed, "success": success, "alerts": alerts}

def get_hourly_data(db_path):
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT strftime('%H:00', timestamp) AS hour,
               COUNT(*) AS total,
               SUM(CASE WHEN status='FAILED' THEN 1 ELSE 0 END) AS failed
        FROM logs
        WHERE timestamp >= datetime('now', '-24 hours')
        GROUP BY hour
        ORDER BY hour
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_top_ips(db_path, limit=10):
    conn = get_db(db_path)
    rows = conn.execute("""
        SELECT ip, COUNT(*) AS attempts,
               SUM(CASE WHEN status='FAILED' THEN 1 ELSE 0 END) AS failed
        FROM logs
        GROUP BY ip
        ORDER BY failed DESC
        LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ── Alert queries ─────────────────────────────────────────────────────────────

def insert_alert(db_path, ip, severity, count, message):
    conn = get_db(db_path)
    conn.execute(
        "INSERT INTO alerts (ip, severity, count, message) VALUES (?, ?, ?, ?)",
        (ip, severity, count, message)
    )
    conn.commit()
    conn.close()

def get_all_alerts(db_path, limit=100):
    conn = get_db(db_path)
    rows = conn.execute(
        "SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def alert_exists_recent(db_path, ip, window_minutes=5):
    conn = get_db(db_path)
    row = conn.execute("""
        SELECT id FROM alerts
        WHERE ip=? AND timestamp >= datetime('now', ? || ' minutes')
    """, (ip, f"-{window_minutes}")).fetchone()
    conn.close()
    return row is not None
