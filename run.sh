#!/bin/bash
echo "======================================"
echo " Starting ATLAS AI Execution Runtime "
echo "======================================"

echo "Cleaning up old processes..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:5173 | xargs kill -9 2>/dev/null

# Start Backend
echo "[1/3] Starting FastAPI Backend on port 8000..."
export OPENROUTER_API_KEY="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"
source hypermemoryai/atlas/bin/activate
if [ -d "browser/atlas-browser" ]; then
    echo "Ensuring browser dependencies are in hypermemoryai venv..."
    pip install -e browser/atlas-browser > /dev/null 2>&1
fi
uvicorn runtime.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Start Frontend
echo "[2/3] Starting Vite + Electron Frontend..."
cd apps/desktop
npm run electron:dev > ../../frontend.log 2>&1 &
FRONTEND_PID=$!

cd ../..

echo "Backend PID: $BACKEND_PID (logs in backend.log)"
echo "Frontend PID: $FRONTEND_PID (logs in frontend.log)"

echo "Waiting for services to initialize..."
sleep 3

echo "[3/3] Waiting for Electron App to Launch..."
echo "The Desktop App window should appear shortly."

echo "======================================"
echo " ATLAS IS RUNNING. PRESS CTRL+C TO QUIT "
echo "======================================"

# Trap ctrl-c and kill background processes
trap "echo 'Shutting down ATLAS...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT TERM

# Tail logs to terminal
tail -f backend.log frontend.log
