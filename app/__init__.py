from flask import Flask
from config import Config
from app.models.log_model import init_db

def create_app():
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    # Initialize database
    with app.app_context():
        init_db(app.config['DATABASE'])

    # Register blueprints
    from app.routes.dashboard import dashboard_bp
    from app.routes.alerts import alerts_bp
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(alerts_bp)

    return app
