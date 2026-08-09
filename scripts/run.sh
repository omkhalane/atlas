#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VSCODE_DIR="$SCRIPT_DIR/apps/vscode"

echo "======================================"
echo "        Starting Atlas IDE            "
echo "======================================"

if [ ! -d "$VSCODE_DIR" ]; then
    echo "Error: Atlas app directory not found at $VSCODE_DIR"
    exit 1
fi

cd "$VSCODE_DIR"

if [ -f "./scripts/code.sh" ]; then
    echo "Starting Atlas Browser Connector..."
    
    # Kill any dangling connector instances
    fuser -k 3210/tcp 2>/dev/null || true
    
    python3 "$SCRIPT_DIR/packages/browser/connector_server.py" &
    CONNECTOR_PID=$!
    
    echo "Starting ATLAS IPC Server..."
    PYTHONPATH="$SCRIPT_DIR:$SCRIPT_DIR/packages" python3 "$SCRIPT_DIR/packages/runtime/server/ipc_server.py" &
    IPC_PID=$!
    
    # Ensure background processes die when this script exits
    trap "kill $CONNECTOR_PID $IPC_PID 2>/dev/null || true" EXIT INT TERM
    
    echo "Launching Atlas IDE application..."
    ./scripts/code.sh "$@" --no-sandbox
    
    echo "Shutting down Atlas IDE..."
    exit 0
else
    echo "Error: ./scripts/code.sh script not found in $VSCODE_DIR"
    exit 1
fi
