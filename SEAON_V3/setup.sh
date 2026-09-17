#!/usr/bin/env bash
# ────────────────────────────────────────────────────────────────
# SEAON Manufacturing Dashboard — One-shot dev setup
# ────────────────────────────────────────────────────────────────
set -e

echo "🔧 Setting up SEAON Manufacturing Dashboard..."

# 1) Backend virtualenv
if [ ! -d "backend/.venv" ]; then
    echo "📦 Creating Python venv..."
    python3 -m venv backend/.venv
fi

echo "📥 Installing backend dependencies..."
source backend/.venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt

# 2) Copy .env if missing
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    echo "📝 Created backend/.env from example — edit SECRET_KEY before production."
fi

# 3) Frontend has no build step (vanilla JS)
echo "✅ Frontend is plain HTML/CSS/JS — no build needed."

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the backend:"
echo "  cd backend && source .venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "To serve the frontend:"
echo "  cd frontend && python3 -m http.server 5500"
echo ""
echo "Or run everything with Docker:"
echo "  docker compose up --build"