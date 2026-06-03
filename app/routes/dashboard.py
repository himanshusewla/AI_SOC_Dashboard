from flask import Blueprint, render_template, current_app, jsonify, g
from app.models.log_model import get_stats, get_hourly_data, get_top_ips, get_all_logs
from app.services.log_generator import generate_sample_logs

dashboard_bp = Blueprint('dashboard', __name__)
_seeded = False

def _seed_once():
    global _seeded
    if not _seeded:
        _seeded = True
        generate_sample_logs(current_app.config['DATABASE'])

@dashboard_bp.route('/')
def index():
    _seed_once()
    db   = current_app.config['DATABASE']
    stats = get_stats(db)
    return render_template('dashboard.html', stats=stats)

@dashboard_bp.route('/api/stats')
def api_stats():
    db = current_app.config['DATABASE']
    return jsonify(get_stats(db))

@dashboard_bp.route('/api/hourly')
def api_hourly():
    db = current_app.config['DATABASE']
    return jsonify(get_hourly_data(db))

@dashboard_bp.route('/api/top-ips')
def api_top_ips():
    db = current_app.config['DATABASE']
    return jsonify(get_top_ips(db))

@dashboard_bp.route('/api/logs')
def api_logs():
    db = current_app.config['DATABASE']
    return jsonify(get_all_logs(db, limit=100))
