#!/bin/bash

# Kill processes on all common development ports
# Usage: ./kill-dev-ports.sh [--force]

set -e

FORCE="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Common development ports
DEV_PORTS=(3000 5000 5001 8000 8080 8888 9000)

echo "🔍 Killing processes on common development ports..."
echo "Ports to check: ${DEV_PORTS[*]}"
echo "================================"

for PORT in "${DEV_PORTS[@]}"; do
    echo "🔄 Checking port $PORT..."
    if [ "$FORCE" = "--force" ]; then
        "$SCRIPT_DIR/kill-port.sh" "$PORT" --force
    else
        "$SCRIPT_DIR/kill-port.sh" "$PORT"
    fi
    echo ""
done

echo "================================"
echo "✅ Finished checking all development ports"
echo "💡 Run './scripts/check-ports.sh' to verify port status"