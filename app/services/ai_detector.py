"""
AI Anomaly Detection — Isolation Forest
========================================
Features used per IP:
  - total_attempts    : how many login attempts from this IP
  - failed_ratio      : % of attempts that failed  (0.0 – 1.0)
  - peak_hour_density : fraction of attempts in the busiest single hour
  - unique_users      : number of distinct usernames tried

An anomaly_score < 0  means Isolation Forest flags it as suspicious.
"""

import sqlite3
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


def _build_features(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    ips = conn.execute("""
        SELECT ip,
               COUNT(*)  AS total,
               SUM(CASE WHEN status='FAILED' THEN 1 ELSE 0 END) AS failed
        FROM logs
        GROUP BY ip
        HAVING total >= 3
    """).fetchall()

    records = []
    for row in ips:
        ip    = row['ip']
        total = row['total']
        failed_ratio = row['failed'] / total if total else 0.0

        hour_row = conn.execute("""
            SELECT strftime('%H', timestamp) AS hr, COUNT(*) AS cnt
            FROM logs WHERE ip=?
            GROUP BY hr ORDER BY cnt DESC LIMIT 1
        """, (ip,)).fetchone()
        peak_hour_density = (hour_row['cnt'] / total) if hour_row else 0.0

        u_row = conn.execute(
            "SELECT COUNT(DISTINCT username) AS u FROM logs WHERE ip=?", (ip,)
        ).fetchone()
        unique_users = u_row['u'] if u_row else 1

        records.append({
            'ip': ip,
            'total': total,
            'failed_ratio': round(failed_ratio, 4),
            'peak_hour_density': round(peak_hour_density, 4),
            'unique_users': unique_users
        })

    conn.close()
    return records


def run_isolation_forest(db_path, contamination=0.15):
    records = _build_features(db_path)
    if len(records) < 4:
        return {"error": "Need at least 4 IPs with 3+ attempts to run AI detection."}

    X = np.array([
        [r['total'], r['failed_ratio'], r['peak_hour_density'], r['unique_users']]
        for r in records
    ], dtype=float)

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    clf = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
    clf.fit(X_scaled)

    predictions = clf.predict(X_scaled)
    scores      = clf.score_samples(X_scaled)

    results = []
    for i, r in enumerate(records):
        results.append({
            'ip':                r['ip'],
            'total_attempts':    r['total'],
            'failed_ratio':      r['failed_ratio'],
            'peak_hour_density': r['peak_hour_density'],
            'unique_users':      r['unique_users'],
            'anomaly':           bool(predictions[i] == -1),
            'anomaly_score':     round(float(scores[i]), 4),
            'risk_label':        _risk_label(scores[i], predictions[i])
        })

    results.sort(key=lambda x: x['anomaly_score'])
    return results


def _risk_label(score, pred):
    if pred == 1:
        return 'NORMAL'
    if score < -0.20:
        return 'CRITICAL'
    if score < -0.10:
        return 'HIGH'
    return 'SUSPICIOUS'
