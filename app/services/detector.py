import sqlite3
from datetime import datetime, timedelta
from app.models.log_model import get_db, insert_alert, alert_exists_recent

THRESHOLDS = {
    'LOW':      (3,  300),   # 3 failures in 5 min
    'MEDIUM':   (5,  120),   # 5 failures in 2 min
    'HIGH':     (10, 60),    # 10 failures in 1 min
    'CRITICAL': (20, 60),    # 20 failures in 1 min
}

def check_brute_force(db_path, ip):
    """
    Check if `ip` has triggered brute-force thresholds.
    Returns (severity, count) or (None, 0).
    """
    conn = get_db(db_path)
    detected = None
    count = 0

    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        max_attempts, window_sec = THRESHOLDS[severity]
        since = datetime.utcnow() - timedelta(seconds=window_sec)
        row = conn.execute("""
            SELECT COUNT(*) FROM logs
            WHERE ip=? AND status='FAILED' AND timestamp >= ?
        """, (ip, since.strftime('%Y-%m-%d %H:%M:%S'))).fetchone()
        cnt = row[0]
        if cnt >= max_attempts:
            detected = severity
            count = cnt
            break

    conn.close()

    if detected and not alert_exists_recent(db_path, ip, window_minutes=5):
        msg = f"Brute-force detected from {ip}: {count} failed attempts"
        insert_alert(db_path, ip, detected, count, msg)

    return detected, count
