# AI-Powered SOC Dashboard — Brute Force Detection

A real-time Security Operations Center (SOC) dashboard that detects brute-force login attacks, displays live analytics, and sends severity-graded alerts.

---

## Features
- ✅ Real-time login monitoring
- ✅ Brute-force detection engine (LOW / MEDIUM / HIGH / CRITICAL)
- ✅ Live dashboard with Charts (hourly activity, top attacking IPs)
- ✅ Severity-filtered alerts page
- ✅ Login simulator (test attacks without real traffic)
- ✅ SQLite database (swap for PostgreSQL in production)
- ✅ Ready for deployment on Render / Railway

---

## Tech Stack
| Layer      | Technology            |
|------------|-----------------------|
| Backend    | Python 3.10+, Flask   |
| Database   | SQLite (dev), PostgreSQL (prod) |
| Frontend   | HTML, CSS, JS, Chart.js |
| Deployment | Render / Railway / VPS |

---

## Local Setup (Windows / Mac / Linux)

### 1. Clone or download the project
```bash
git clone https://github.com/Yhimanshusewla/AI_SOC_Dashboard.git
cd AI_SOC_Dashboard
```

### 2. Create virtual environment
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the app
```bash
python run.py
```

### 5. Open browser
```
http://localhost:5000
```

---

## Folder Structure
```
AI_SOC_Dashboard/
├── run.py                  # App entry point
├── config.py               # Configuration
├── requirements.txt
├── README.md
├── app/
│   ├── __init__.py         # Flask factory
│   ├── routes/
│   │   ├── dashboard.py    # Dashboard routes
│   │   └── alerts.py       # Alerts + login API
│   ├── models/
│   │   └── log_model.py    # SQLite DB functions
│   ├── services/
│   │   ├── detector.py     # Brute-force detection
│   │   └── log_generator.py # Sample data seeder
│   ├── templates/
│   │   ├── dashboard.html
│   │   └── alerts.html
│   └── static/
│       ├── css/style.css
│       └── js/dashboard.js
├── database/
│   └── soc.db              # Auto-created
└── logs/
    └── auth.log
```

---

## Detection Logic

| Severity | Threshold           |
|----------|---------------------|
| LOW      | 3 failures / 5 min  |
| MEDIUM   | 5 failures / 2 min  |
| HIGH     | 10 failures / 1 min |
| CRITICAL | 20 failures / 1 min |

---

## API Endpoints

| Method | Endpoint       | Description              |
|--------|----------------|--------------------------|
| GET    | /              | Dashboard page           |
| GET    | /alerts        | Alerts page              |
| GET    | /api/stats     | Summary stats (JSON)     |
| GET    | /api/hourly    | Hourly login data (JSON) |
| GET    | /api/top-ips   | Top attacking IPs (JSON) |
| GET    | /api/logs      | Recent logs (JSON)       |
| GET    | /api/alerts    | All alerts (JSON)        |
| POST   | /api/login     | Simulate a login attempt |

### POST /api/login example:
```json
{
  "username": "admin",
  "ip": "45.33.32.156",
  "status": "FAILED"
}
```

---

## Deploy on Render (Free)

1. Push code to GitHub:
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/himanshuseewla/AI_SOC_Dashboard.git
git push -u origin main
```

2. Go to https://render.com → New → Web Service
3. Connect your GitHub repo
4. Set:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn run:app`
5. Click **Deploy**

Your live URL: `https://your-soc-dashboard.onrender.com`

---

## Author
Built with Flask + SQLite + Chart.js
