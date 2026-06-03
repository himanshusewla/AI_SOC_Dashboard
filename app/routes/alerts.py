from flask import Blueprint, render_template, request, jsonify, current_app
from app.models.log_model import insert_log, get_all_alerts
from app.services.detector import check_brute_force
from app.services.ai_detector import run_isolation_forest

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/alerts')
def alerts():
    db = current_app.config['DATABASE']
    all_alerts = get_all_alerts(db)
    return render_template('alerts.html', alerts=all_alerts)

@alerts_bp.route('/api/alerts')
def api_alerts():
    db = current_app.config['DATABASE']
    return jsonify(get_all_alerts(db))

@alerts_bp.route('/api/login', methods=['POST'])
def api_login():
    """Simulate a login attempt and run brute-force detection."""
    data = request.get_json(force=True)
    username = data.get('username', 'unknown')
    ip       = data.get('ip', '0.0.0.0')
    status   = data.get('status', 'FAILED').upper()

    db = current_app.config['DATABASE']
    insert_log(db, username, ip, status)

    severity, count = check_brute_force(db, ip)

    return jsonify({
        'logged': True,
        'alert': severity,
        'count': count,
        'message': f"Alert: {severity} - {count} failures from {ip}" if severity else "No alert"
    })

@alerts_bp.route('/api/ai-detect')
def api_ai_detect():
    """Run Isolation Forest on all IPs and return anomaly results."""
    db = current_app.config['DATABASE']
    result = run_isolation_forest(db)
    return jsonify(result)
