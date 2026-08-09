#!/usr/bin/env bash

set -e

echo "Stopping any running ATLAS IDE instances..."
killall electron 2>/dev/null || true
killall code 2>/dev/null || true
pkill -f connector_server.py 2>/dev/null || true
fuser -k 3210/tcp 2>/dev/null || true
fuser -k 50051/tcp 2>/dev/null || true

echo "Wiping user data and settings to force new onboarding..."
rm -rf ~/.vscode-oss-dev
rm -rf ~/.vscode-oss-shared
rm -rf ~/.config/Code\ -\ OSS\ -\ Dev
rm -rf ~/.atlas 2>/dev/null || true

if [ "$1" == "--hard" ]; then
    echo "Hard reset requested: Wiping dependencies and compiled files..."
    echo "After this, you will need to run the setup process like a freshly cloned repository."
    
    cd /code/ATLAS
    
    echo "Cleaning Python environment..."
    rm -rf .venv/
    find . -type d -name "__pycache__" -exec rm -rf {} +
    
    echo "Cleaning VS Code build and node_modules..."
    cd /code/ATLAS/apps/vscode
    rm -rf out/
    rm -rf .build/
    rm -rf node_modules/
    
    echo "Cleaning Extension dependencies..."
    rm -rf extensions/copilot/node_modules/
    
    echo "Hard reset complete. Please re-run npm install and python setup."
    exit 0
fi

echo "Done! You can now run ./scripts/run.sh to start a fresh test."
