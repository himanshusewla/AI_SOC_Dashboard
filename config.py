import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'soc-dashboard-secret-2024')
    DATABASE = os.path.join(BASE_DIR, 'database', 'soc.db')
    LOG_FILE = os.path.join(BASE_DIR, 'logs', 'auth.log')
    BRUTE_FORCE_THRESHOLD = 5       # failed attempts
    BRUTE_FORCE_WINDOW = 60         # seconds
    DEBUG = True
