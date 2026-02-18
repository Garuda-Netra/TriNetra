

# Trinetra (त्रिनेत्र) — Third Eye Port Scanner

> **_"We worship the three-eyed One (Lord Shiva) who is fragrant and nourishes all."_**  
> **_"May He liberate us from the bondage of death."_** — Rig Veda (7.59.12)

**Created by [Garuda Netra](https://github.com/Garuda-Netra)**

Trinetra is a full-stack port scanner with dual interfaces:

- **CLI**: Fast, scriptable command-line scanning with Rich progress bars
- **Django Web GUI**: Beautiful, interactive web dashboard with history & export
- **Shared Backend**: Single scanning engine for both interfaces
- **Production-Ready**: Configured for Render, Heroku, PythonAnywhere, and custom hosting

## ✨ Features

### CLI (`python main.py`)
- **Fast TCP scanning** with socket-level performance
- **Rich terminal UI**: Colored output, progress bars, ASCII art banner
- **Service detection**: Identifies common services (SSH, HTTP, MySQL, etc.)
- **Persistent storage**: Results auto-saved to SQLite database
- **Flexible input**: Port ranges (`20-100`), comma-separated (`22,80,443`), or mixed
- **Timeout control**: Adjustable socket timeout (default: 0.5s)
- **SQL export**: All scans stored for historical analysis

### Django Web GUI (`http://localhost:8000`)
- **Interactive scan form**: Enter target and ports in-browser
- **Live results table**: Real-time port status with service names
- **Scan history**: View, filter, and export past scans
- **Date/target filters**: Narrow down historical scans
- **CSV/JSON export**: Download scan results in multiple formats
- **Responsive design**: Works on desktop and mobile
- **Dark theme**: Sanskrit-inspired aesthetic with Trinetra branding
- **Animations**: Smooth cursor trail and glowing effects

### Shared Backend
- Unified scanning engine (`TriNetra/scanner.py`)
- Common service name mapping (`scanner/services.py`)
- Centralized database (`data/trinetra_scans.db`)

## Project Structure

```text
TriNetra/
├── main.py
├── manage.py
├── requirements.txt
├── README.md
├── static/
│   ├── img/
│   │   └── trinetra-eye.svg
│   └── js/
│       └── cursor-trail.js
├── templates/
│   ├── base.html
│   └── scanner/
│       ├── history.html
│       └── scan.html
├── trinetra/
│   ├── __init__.py
│   ├── cli.py
│   ├── database.py
│   ├── scanner.py
│   └── ui.py
├── trinetra_web/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── scanner/
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── forms.py
    ├── models.py
    ├── urls.py
    ├── views.py
    └── migrations/
        └── __init__.py
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+ (recommended: 3.11.6 for Render compatibility)
- pip or conda

### Local Installation

**1) Clone the repository**
```bash
git clone https://github.com/Garuda-Netra/TriNetra.git
cd TriNetra
```

**2) Create virtual environment**
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

**3) Install dependencies**
```bash
pip install -r requirements.txt
```

**4) (Optional) Configure environment**
```bash
# Create .env file (or copy from .env.example)
cp .env.example .env
# Edit .env with your settings
```

## 📋 Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `DEBUG` | `True` | Django debug mode (set to `false` in production) |
| `SECRET_KEY` | `django-insecure-...` | Django secret key (generate new for production) |
| `ALLOWED_HOSTS` | `127.0.0.1,localhost` | Allowed domains for Django |
| `CSRF_TRUSTED_ORIGINS` | `http://127.0.0.1:8000` | CSRF-safe origins |
| `DATABASE_URL` | (empty) | PostgreSQL URL (auto-detects if set) |

Generate a secure `SECRET_KEY`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

## 🖥️ Usage

### CLI Scanner

**Basic scan:**
```bash
python main.py scanme.nmap.org 20-100
```

**Custom timeout and database:**
```bash
python main.py 127.0.0.1 22,80,443 --timeout 1.0 --db data/scans.db
```

**Help:**
```bash
python main.py --help
```

**Output example:**
╔════════════════════════════════════════════════════==============+
|                                                                  |
| ████████╗██████╗ ██╗███╗   ██╗███████╗████████╗██████╗  █████╗   |
| ╚══██╔══╝██╔══██╗██║████╗  ██║██╔════╝╚══██╔══╝██╔══██╗██╔══██╗  |
|    ██║   ██████╔╝██║██╔██╗ ██║█████╗     ██║   ██████╔╝███████║  |
|    ██║   ██╔══██╗██║██║╚██╗██║██╔══╝     ██║   ██╔══██╗██╔══██║  |
|    ██║   ██║  ██║██║██║ ╚████║███████╗   ██║   ██║  ██║██║  ██║  |
|    ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝  |
|                                                                  |
│  TRINETRA — Third Eye Port Scanner                               |
╚════════════════════════════════════════════════════===============

⚡ Scan Configuration
─────────────────────────────
Target : scanme.nmap.org
IP     : 45.33.32.156
Ports  : 100

Port   Service      Version                      Status
22     ssh          -                            OPEN
80     http         -                            OPEN
443    https        -                            OPEN
```

### Django Web Interface

**Start development server:**
```bash
python manage.py runserver
```

**Access:**
- **Scan page**: http://127.0.0.1:8000/
- **History page**: http://127.0.0.1:8000/history/

**Workflow:**
1. Enter target and ports on the Scan page
2. Click **"⚡ Scan"**
3. Wait for results (live progress shown)
4. View results in the table
5. **Export Latest CSV/JSON** (bottom of page)
6. Go to **"◈ History"** to filter and export past scans

## 🗄️ Database

### SQLite (Default - Local Development)
- File: `data/trinetra_scans.db`
- Table: `scans` (id, target, port, status, timestamp)
- Perfect for CLI use and small deployments
- **Limitation**: Ephemeral storage on PaaS (Heroku, Render) lose data on restart

### PostgreSQL (Production Recommended)
- Set `DATABASE_URL` environment variable
- Auto-detected by Django settings
- Persistent data storage
- Supports concurrent access better
- Recommended for production deployments

**Switch to PostgreSQL:**
```bash
# Install driver
pip install psycopg[binary]

# Set environment variable
export DATABASE_URL=postgresql://user:password@host:5432/trinetra

# No code changes needed!
```

## 🔒 Security

- **Always scan only systems you own or have explicit written permission to test**
- Unauthorized port scanning may violate laws in your jurisdiction
- Use reasonable timeout values to avoid unnecessary network load
- In production, set `DEBUG=False` and generate a strong `SECRET_KEY`
- Enable HTTPS/SSL in production (`SECURE_SSL_REDIRECT=true`)
- Use environment variables for sensitive data (never commit `.env`)

## 📄 License

This project is created by [Garuda Netra](https://github.com/Garuda-Netra). Check repository for license details.

## 🙏 Attribution

Built with:
- **Django** — Web framework
- **Rich** — Beautiful terminal output
- **Tailwind CSS** — Responsive UI styling
- **SQLite/PostgreSQL** — Data persistence
- **Gunicorn** — Production WSGI server

Inspired by the **Mahamrityunjaya Mantra** from the Rig Veda (7.59.12)

## 🌐 Deployment

### Deploy on Render (Recommended for beginners)

**1) Push to GitHub**
```bash
git add .
git commit -m "Deploy to Render"
git push origin main
```

**2) Create Render account & Web Service**
- Go to [render.com](https://render.com)
- Click **"New +"** → **"Web Service"**
- Select your GitHub repo: `Garuda-Netra/TriNetra`

**3) Configure Web Service**
| Field | Value |
|-------|-------|
| **Name** | `trinetra` |
| **Environment** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput` |
| **Start Command** | `gunicorn trinetra_web.wsgi --log-file -` |

**4) Add Environment Variables** (click "Environment")
```
SECRET_KEY = <generate-random-key>
DEBUG = false
ALLOWED_HOSTS = trinetra-xxxxx.onrender.com
CSRF_TRUSTED_ORIGINS = https://trinetra-xxxxx.onrender.com
```

**5) (Optional) Attach PostgreSQL**
- Click **"Create"** → **"PostgreSQL"**
- Render auto-populates `DATABASE_URL` in your Web Service
- Your app will auto-detect and use it

**6) Deploy**
- Click **"Create Web Service"**
- Wait for build (2–5 minutes)
- Check **"Logs"** tab for status

**Success indicator:**
```
Starting gunicorn 22.0.0
Listening at: 0.0.0.0:10000
```

### Deploy on Heroku

`Procfile` is included: `web: gunicorn trinetra_web.wsgi --log-file -`

```bash
# Install Heroku CLI
heroku login
heroku create trinetra-app
git push heroku main

# Set config vars
heroku config:set DEBUG=false SECRET_KEY=<your-key> ALLOWED_HOSTS=<your-domain>

# Collect static
heroku run python manage.py collectstatic --noinput
```

### Deploy on PythonAnywhere

1. Upload/clone project to PythonAnywhere
2. Create virtualenv: `mkvirtualenv --python=/usr/bin/python3.9 trinetra`
3. Install: `pip install -r requirements.txt`
4. Set environment variables in web app settings
5. Set WSGI file to `trinetra_web.wsgi`
6. Run: `python manage.py collectstatic --noinput`

### Deploy on Digital Ocean / Custom VPS

```bash
# On server
git clone https://github.com/Garuda-Netra/TriNetra.git
cd TriNetra
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 trinetra_web.wsgi

# Or with Nginx reverse proxy (recommended for production)
```

### Use PostgreSQL (Recommended for production)

If you haven't attached a database:

```bash
# Set DATABASE_URL environment variable
export DATABASE_URL=postgresql://user:password@host:5432/trinetra

# Install PostgreSQL driver
pip install psycopg[binary]

# No code changes needed—settings auto-detect!
```
