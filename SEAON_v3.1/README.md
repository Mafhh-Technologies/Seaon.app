# SEAON ERP — Django + SQLite

This version removes the old Flask backend and serves the SEAON frontend and Django API from one process.

## Start everything

### Windows
Double-click `run_seaon_windows.bat`.

### Manual
```powershell
cd Backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:8000/app/login.html`.

Demo:
- Email: `admin@seaon.com`
- Password: `Admin@123`

## URLs
- Application: `http://127.0.0.1:8000/app/login.html`
- API: `http://127.0.0.1:8000/api/`
- API health: `http://127.0.0.1:8000/api/health/`
- Django admin: `http://127.0.0.1:8000/admin/`

## Project layout
- `Backend/app.py` — single startup entry point
- `Backend/manage.py` — standard Django CLI
- `Backend/config/` — Django configuration
- `Backend/erp/` — models, API, auth, permissions and services
- `Backend/public/` — frontend HTML/CSS/JS
- `Backend/seaon.db` — SQLite database

The frontend no longer depends on a separate frontend server. CSS and JavaScript are served by Django, and browser requests use `/api/...`, so there is no hard-coded `localhost:3000` or cross-server path mismatch.

For production, change the development secret, DEBUG, CORS, ALLOWED_HOSTS and demo credentials.
