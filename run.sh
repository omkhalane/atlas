#!/usr/bin/env bash

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
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
    echo "Launching Atlas IDE application..."
    exec ./scripts/code.sh "$@"
else
    echo "Error: ./scripts/code.sh script not found in $VSCODE_DIR"
    exit 1
fi
