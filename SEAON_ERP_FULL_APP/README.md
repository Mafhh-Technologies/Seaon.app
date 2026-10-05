# SEAON ERP — Simple Windows Application

SEAON is a Django + SQLite ERP for manufacturing, stock and warehouse operations.

## The only thing a normal user needs to know

### Windows
Double-click:

`run_seaon_windows.bat`

The script creates the environment, installs the packages and starts the whole application.

Then open:

`http://127.0.0.1:8000/app/login.html`

### Default administrator
Email: `admin@seaon.com`
Password: `Admin@123`

## How the application works

There is one backend process:

`Backend/app.py`

It automatically:

1. Runs Django migrations.
2. Creates the default administrator and roles.
3. Imports the supplied Excel stock sheets.
4. Creates FIFO opening batches.
5. Starts the Django server.

The browser frontend and Django API are served by the same server.

## Main screens

- Dashboard — KPIs and operational health
- Inventory — stock and adjustments
- Orders — manufactured/readymade orders
- Production — work orders
- BOM / Materials — material mapping
- Warehouse — inward, putaway, pick, pack and dispatch
- Returns — return/repair/replacement/redelivery workflow
- FIFO Batches — oldest stock first
- Reports — management summaries
- Alerts — low/dead/near-expiry stock
- Admin Panel — users, roles, permissions, imported stock and audit log

## Admin Panel

Open:

`http://127.0.0.1:8000/app/admin.html`

Only Super Admin/Admin accounts can enter it.

The Super Admin can:
- create users
- activate/deactivate users
- assign roles
- create custom roles
- choose permissions
- inspect imported spreadsheet data
- re-import Excel data
- review audit logs

## Supplied sample data

The Excel files are stored in:

`Backend/sample_data/`

They are imported into SQLite automatically when `app.py` starts.

The original spreadsheet row is retained in `StockRecord` with:
- source file
- sheet
- source row
- category
- item
- size
- colour
- thickness
- width
- length
- minimum stock
- available stock
- required stock
- remarks

Imported stock is also converted into products/inventory and opening FIFO batches so the software can be tested immediately.

## Database

SQLite file:

`Backend/seaon.db`

You do not need to create it manually.

## Developer commands

```powershell
cd Backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_seaon
python manage.py import_sample_data
python manage.py runserver
```

Normal operation should use `python app.py`.

## Important URLs

- ERP: `http://127.0.0.1:8000/app/login.html`
- Admin panel: `http://127.0.0.1:8000/app/admin.html`
- Django technical admin: `http://127.0.0.1:8000/admin/`
- API health: `http://127.0.0.1:8000/api/health/`

## Source of the business design

The supplied `SEAON - DASHBOARD Requirements.pdf` is included under `Backend/docs/`.
The implementation covers the requested Super Admin, role permissions, order flows, returns,
product types, BOM mapping, FIFO inventory, production, warehouse, alerts and role-aware dashboards.

For production deployment, change the development secret, DEBUG, allowed hosts, CORS settings
and demo credentials.
