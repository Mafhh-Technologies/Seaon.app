# SEAON Project Guide

If you are not a programmer, remember these three things:

1. `app.py` starts everything.
2. `public/` is the website users see.
3. `erp/` contains the business rules and database API.

## File responsibilities

- `app.py` — one-click startup.
- `manage.py` — standard Django maintenance commands.
- `config/settings.py` — Django configuration and SQLite.
- `config/urls.py` — connects browser URLs and API URLs.
- `erp/models.py` — database tables.
- `erp/serializers.py` — converts database records to/from API JSON.
- `erp/views.py` — API endpoints.
- `erp/services.py` — business logic such as FIFO.
- `erp/permissions.py` — role/permission checks.
- `erp/admin_api.py` — friendly admin-panel API.
- `erp/management/commands/seed_seaon.py` — creates demo administrator, roles and base data.
- `erp/management/commands/import_sample_data.py` — imports supplied Excel files.
- `public/login.html` — login page.
- `public/index.html` — main ERP shell.
- `public/admin.html` — Super Admin panel.
- `public/JS/api.js` — all browser-to-server requests.
- `public/JS/auth.js` — login/session handling.
- `public/JS/app.js` — all ERP screens and button actions.
- `public/JS/admin.js` — admin-panel screens and actions.
- `public/CSS/style.css` — complete application styling.

## Data flow

Button → `app.js` → `api.js` → Django URL → Django view/service → SQLite model.

Keep this flow when adding features. It prevents the frontend and backend from becoming disconnected.
