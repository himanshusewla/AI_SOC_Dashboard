"""
Generates realistic auth log entries for demo / testing.
Call generate_sample_logs() once to seed the DB.
"""
import random
from datetime import datetime, timedelta
from app.models.log_model import insert_log, get_db

USERNAMES = ['admin', 'root', 'user', 'test', 'ubuntu', 'pi', 'oracle',
             'postgres', 'guest', 'deploy', 'jenkins', 'ansible']

NORMAL_IPS  = [f"192.168.1.{i}" for i in range(1, 20)]
ATTACK_IPS  = ['45.33.32.156', '103.21.244.0', '185.220.101.5',
               '198.51.100.42', '203.0.113.77', '91.108.4.0']

def _random_ip(attack=False):
    if attack:
        return random.choice(ATTACK_IPS)
    return random.choice(NORMAL_IPS + ATTACK_IPS[:1])

def generate_sample_logs(db_path, num_logs=300):
    """Seed DB with realistic mixed log entries."""
    now = datetime.utcnow()
    conn = get_db(db_path)
    existing = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    conn.close()
    if existing > 50:
        return  # already seeded

    entries = []

    # Normal traffic
    for _ in range(int(num_logs * 0.6)):
        ts = now - timedelta(minutes=random.randint(0, 1440))
        ip = random.choice(NORMAL_IPS)
        user = random.choice(USERNAMES)
        status = random.choices(['SUCCESS', 'FAILED'], weights=[85, 15])[0]
        entries.append((user, ip, status, ts.strftime('%Y-%m-%d %H:%M:%S')))

    # Brute-force bursts from attack IPs
    for attacker in ATTACK_IPS[:3]:
        burst_time = now - timedelta(minutes=random.randint(5, 60))
        for i in range(random.randint(15, 30)):
            ts = burst_time + timedelta(seconds=i * 2)
            user = random.choice(['admin', 'root'])
            entries.append((user, attacker, 'FAILED', ts.strftime('%Y-%m-%d %H:%M:%S')))
        # occasional success after burst
        entries.append(('admin', attacker, 'SUCCESS', (burst_time + timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')))

    random.shuffle(entries)
    conn = get_db(db_path)
    conn.executemany(
        "INSERT INTO logs (username, ip, status, timestamp) VALUES (?, ?, ?, ?)",
        entries
    )
    conn.commit()
    conn.close()
