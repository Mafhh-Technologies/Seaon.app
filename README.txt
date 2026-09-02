SEON ERP - FIXED BACKEND CONNECTED VERSION
===========================================

THIS VERSION FIXES THE "SERVER REQUEST FAILED" PROBLEM.

IMPORTANT:
Do NOT double-click templates/index.html.
Run Flask and open:
    http://127.0.0.1:5000

PROJECT STRUCTURE
-----------------
app.py                    Flask server + REST API
 database.py              SQLite connection helper
database.sql              Database schema
 database.db              SEON product database (preloaded)
templates/index.html      Frontend page
static/style.css          Frontend CSS
static/script.js          Frontend JavaScript
requirements.txt          Python dependency
start.bat                 Windows one-click-ish starter

WHY THE OLD VERSION FAILED
---------------------------
1. There were multiple versions of index.html and script.js.
2. Some versions used relative files such as script.js while Flask expects
   static files under /static.
3. One frontend version only pushed products into a JavaScript array and did
   not save them to SQLite.
4. The browser will fail if index.html is opened with file:// because the
   frontend is designed to call the Flask API.
5. The new version uses one clear API path and Flask serves the HTML, CSS and JS.

SETUP - WINDOWS
---------------
1. Open this folder in VS Code.
2. Open Terminal.
3. Run:
       py -m venv .venv
       .venv\Scripts\activate
       pip install -r requirements.txt
4. Start server:
       python app.py
5. Open:
       http://127.0.0.1:5000

OR simply double-click start.bat.

TEST BACKEND
------------
Open this in browser:
    http://127.0.0.1:5000/api/health

You should see JSON similar to:
    {"status":"ok","database":"connected","products":165}

PRODUCT FLOW
------------
Add Product
    Browser JS -> POST /api/products -> Flask -> SQLite INSERT

Edit Product
    Browser JS -> PUT /api/products/<id> -> Flask -> SQLite UPDATE

Adjust Stock
    Browser JS -> PATCH /api/products/<id>/stock -> Flask -> SQLite UPDATE
    and a stock_movements history row is created.

Delete Product
    Browser JS -> DELETE /api/products/<id> -> Flask -> SQLite DELETE

The page reloads the data from SQLite after every successful operation.

DATABASE
--------
products = current inventory master data.
stock_movements = stock adjustment history.

The supplied SEON data remains in database.db. The initial database contains
165 imported product records.

BACKUP
------
Before major changes, copy database.db somewhere safe.
SQLite is a single-file database, so this is easy.

NEXT MODULES
------------
After Inventory is stable, add these as separate tables:
- customers
- orders
- order_items
- bom_headers
- bom_items
- production_orders
- suppliers
- purchase_orders

Do not put Orders, BOM and Production fields into products.
