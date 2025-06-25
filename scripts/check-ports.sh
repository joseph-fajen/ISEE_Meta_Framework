#!/bin/bash

# Check status of common development ports
# Usage: ./check-ports.sh [port1] [port2] [...]

set -e

# Default common development ports
DEFAULT_PORTS=(3000 5000 5001 8000 8080 8888 9000)

# Use provided ports or defaults
if [ $# -eq 0 ]; then
    PORTS=("${DEFAULT_PORTS[@]}")
else
    PORTS=("$@")
fi

echo "🔍 Checking port status..."
echo "================================"

# Track if any ports are in use
PORTS_IN_USE=false

for PORT in "${PORTS[@]}"; do
    # Validate port is numeric
    if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
        echo "⚠️  Skipping invalid port: $PORT"
        continue
    fi
    
    # Check if port is in use
    PROCESSES=$(lsof -ti tcp:$PORT 2>/dev/null || true)
    
    if [ -z "$PROCESSES" ]; then
        echo "✅ Port $PORT: Available"
    else
        echo "🔴 Port $PORT: In use"
        PORTS_IN_USE=true
        
        # Show process details
        echo "   Process details:"
        lsof -i tcp:$PORT | while IFS= read -r line; do
            echo "   $line"
        done
        echo ""
    fi
done

echo "================================"

if [ "$PORTS_IN_USE" = true ]; then
    echo "💡 To kill processes on a specific port: ./scripts/kill-port.sh <port>"
    echo "💡 To kill all processes on development ports: ./scripts/kill-dev-ports.sh"
else
    echo "✅ All checked ports are available!"
fi