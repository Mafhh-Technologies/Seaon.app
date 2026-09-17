# SEAON Manufacturing Dashboard

Full-stack manufacturing dashboard for inventory, production, orders, and BOM.

## Stack

- **Backend:** FastAPI · SQLAlchemy 2.0 · SQLite (dev) · JWT auth
- **Frontend:** Vanilla HTML/CSS/JS (no framework, no build step)
- **Deployment:** Docker Compose

## Features

- 🔐 JWT authentication with role-based access (`admin`, `manager`, `operator`, `viewer`)
- 📦 Inventory with FIFO batch tracking and low-stock alerts
- 🏭 Production job scheduling and progress tracking
- 🧾 **Smart Order validation** — checks BOM material availability before creating orders
- 🧮 Bill of Materials (BOM) editor
- 📊 Dashboard with real-time KPIs
- 📤 CSV export

## Quick Start (Docker)

```bash
docker compose up --build