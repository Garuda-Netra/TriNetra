# Trinetra (Third Eye) - CLI + Django GUI Port Scanner

Trinetra is a Python port scanner with:

- CLI layer (argparse + rich output)
- Django GUI layer (TailwindCSS-styled interface)
- Shared scanning backend (`trinetra/scanner.py`)
- Shared SQLite storage (`data/trinetra_scans.db`, table: `scans`)

## Features

### CLI
- `argparse`-based input (`target`, `ports`, optional timeout/db path)
- TCP port scanning using Python `socket`
- ASCII banner + colored output + progress bar (`rich`)
- Results saved to SQLite and summarized after scan

### GUI (Django + TailwindCSS)
- Scan form: target, ports, timeout
- Scan execution via existing scanner backend logic
- Results table: port, service name, open/closed status, timestamp
- History page with dynamic filters by target and date range
- Export filtered history or latest scan as CSV/JSON
- Sanskrit-inspired header/theme, Trinetra logo, and smooth cursor trail animation

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

## Setup (Reproducible)

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Optional env file setup:

```bash
# Windows PowerShell
Copy-Item .env.example .env
# Linux/macOS
cp .env.example .env
```

## Run CLI

```bash
python main.py <target> <ports> [--timeout 0.5] [--db data/trinetra_scans.db]
```

Examples:

```bash
python main.py scanme.nmap.org 20-100
python main.py 127.0.0.1 22,80,443 --timeout 1.0
```

## Run Django GUI

```bash
python manage.py runserver
```

Open:

- Scan page: `http://127.0.0.1:8000/`
- History page: `http://127.0.0.1:8000/history/`

## GUI Flow

1. Enter target and ports on scan page.
2. Click **Scan**.
3. The app reuses existing modules:
   - scanning: `trinetra/scanner.py`
   - DB writes: `trinetra/database.py`
4. Results are stored in SQLite table `scans` and shown with mapped service names.
5. Export latest result set from scan page (CSV/JSON).
6. Use history filters (target/date range) to query past scans dynamically.
7. Export filtered history results (CSV/JSON).

## Service Mapping

Common ports are mapped to service names in `scanner/services.py` (examples):

- `22` → `SSH`
- `80` → `HTTP`
- `443` → `HTTPS`
- `3306` → `MySQL`

Unmapped ports are shown as `Unknown`.

## Export Usage

- On scan page, use **Export Latest CSV** or **Export Latest JSON**.
- On history page, apply target/date-range filters and use:
    - **Export Filtered CSV**
    - **Export Filtered JSON**

Downloads are generated from the same shared SQLite data source.

## Database Schema (Shared)

SQLite table: `scans`

- `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
- `target` (TEXT)
- `port` (INTEGER)
- `status` (TEXT: OPEN/CLOSED)
- `timestamp` (TEXT, ISO-8601 UTC)

## Security Notes

- Scan only systems you own or have explicit authorization to test.
- Keep scan ranges reasonable to avoid unnecessary network impact.
- Default timeout is conservative to prevent excessive hanging requests.

## Deployment (Production-Oriented)

### Production settings already prepared

`trinetra_web/settings.py` supports environment-based production configuration:

- `DEBUG`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `CSRF_TRUSTED_ORIGINS`
- `DATABASE_URL` (optional PostgreSQL)
- `SECURE_SSL_REDIRECT`

Static asset handling is configured for deployment:

- `STATICFILES_DIRS` for project static files
- `STATIC_ROOT` for collected static artifacts
- WhiteNoise middleware for static serving
- Manifest static storage for cache-friendly filenames

Collect static assets before deployment:

```bash
python manage.py collectstatic --noinput
```

### Deploy on PythonAnywhere (simple path)

1. Upload/clone project.
2. Create and activate virtualenv.
3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4. Configure environment variables (`DEBUG=False`, `SECRET_KEY`, `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`).
5. Point WSGI to `trinetra_web.wsgi`.
6. Run:
    ```bash
    python manage.py collectstatic --noinput
    ```
7. Reload app from dashboard.

### Deploy on Heroku / Heroku-like PaaS

`Procfile` is included:

- `web: gunicorn trinetra_web.wsgi --log-file -`

Set config vars:

- `DEBUG=False`
- `SECRET_KEY=<strong secret>`
- `ALLOWED_HOSTS=<your-domain>`
- `CSRF_TRUSTED_ORIGINS=https://<your-domain>`

Then run:

```bash
python manage.py collectstatic --noinput
```

Note: SQLite is fine for demos/small local deployments, but PaaS ephemeral storage makes PostgreSQL better for real production.

## PostgreSQL Switch (Real Deployment)

Current default DB is SQLite for simplicity. To move to PostgreSQL:

1. Provision a PostgreSQL instance.
2. Set `DATABASE_URL`, example:
    ```bash
    DATABASE_URL=postgresql://user:password@host:5432/trinetra
    ```
3. Install driver in deployment environment (if not preinstalled):
    ```bash
    pip install psycopg[binary]
    ```
4. Restart app service.

No code changes are required because settings auto-detect `DATABASE_URL`.

## Exam / Interview Presentation Script

### 1) Opening (20–30 sec)

"Trinetra is a modular cybersecurity project with CLI and Django GUI layers. Both interfaces reuse the same scanner core and the same database module, demonstrating clean architecture and code reuse."

### 2) CLI Demo (1–2 min)

Run:

```bash
python main.py 127.0.0.1 22-30 --timeout 0.3
```

Talk track:

- Arguments are parsed with `argparse`.
- Port probing uses Python `socket`.
- Output is styled (`rich` banner, colors, progress).
- Results are inserted into SQLite `scans` table.

### 3) GUI Demo (2–3 min)

1. Open `/` (scan page), run a localhost scan.
2. Show table columns: port, mapped service, status, timestamp.
3. Export latest scan as CSV/JSON.
4. Open `/history/`, apply target + date-range filters.
5. Show dynamic updates and filtered export.

### 4) Branding + UX (20–30 sec)

- Show Trinetra logo and Sanskrit-inspired header.
- Show cursor trail animation.
- Mention responsive Tailwind-styled forms and tables.

### 5) Ethics Statement (20–30 sec)

"I demonstrate Trinetra only on localhost or authorized systems. Unauthorized scanning is prohibited and may violate law, policy, and responsible security practice."

## Ethical Considerations of Port Scanning

- Only scan assets you own or are explicitly authorized to test.
- Prefer localhost/lab ranges for classroom and interview demos.
- Keep scan range and rate controlled to avoid disruption.
- Respect legal frameworks, organizational policy, and disclosure norms.
- Never use this tool for unauthorized reconnaissance.

## Screenshot Placeholders (for report/slides)

1. **CLI Output Screenshot**
    - Banner + progress + summary + DB save confirmation.
2. **GUI Scan Page Screenshot**
    - Input form + result table with service mapping + export buttons.
3. **GUI History Page Screenshot**
    - Target/date-range filters + filtered results + export options.

## Deployment Health Checks

```bash
python manage.py check
python manage.py collectstatic --noinput
```
