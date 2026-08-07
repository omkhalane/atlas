#!/usr/bin/env bash

set -e

echo "Stopping any running ATLAS IDE instances..."
killall electron 2>/dev/null || true
killall code 2>/dev/null || true
pkill -f connector_server.py 2>/dev/null || true
fuser -k 3210/tcp 2>/dev/null || true

echo "Wiping user data and settings to force new onboarding..."
rm -rf ~/.vscode-oss-dev
rm -rf ~/.vscode-oss-shared
rm -rf ~/.config/Code\ -\ OSS\ -\ Dev

if [ "$1" == "--hard" ]; then
    echo "Hard reset requested: Wiping compiled files..."
    cd /code/ATLAS/apps/vscode
    rm -rf out/
    rm -rf .build/
    
    echo "Recompiling fresh..."
    npm run build-fast
fi

echo "Done! You can now run ./scripts/run.sh to start a fresh test."
