#!/bin/bash

# Kill processes running on a specific port
# Usage: ./kill-port.sh <port> [--force]

set -e

PORT="$1"
FORCE="$2"

if [ -z "$PORT" ]; then
    echo "Usage: $0 <port> [--force]"
    echo "Example: $0 5001"
    echo "Example: $0 5001 --force (use SIGKILL instead of SIGTERM)"
    exit 1
fi

# Check if port is numeric
if ! [[ "$PORT" =~ ^[0-9]+$ ]]; then
    echo "Error: Port must be a number"
    exit 1
fi

echo "🔍 Checking for processes on port $PORT..."

# Find processes using the port
PIDS=$(lsof -ti tcp:$PORT 2>/dev/null || true)

if [ -z "$PIDS" ]; then
    echo "✅ No processes found on port $PORT"
    exit 0
fi

echo "📋 Found processes on port $PORT:"
lsof -i tcp:$PORT

echo ""
echo "🔄 PIDs to terminate: $PIDS"

# Determine signal to use
if [ "$FORCE" = "--force" ]; then
    SIGNAL="KILL"
    echo "⚠️  Using SIGKILL (force kill)"
else
    SIGNAL="TERM"
    echo "🔄 Using SIGTERM (graceful shutdown)"
fi

# Kill the processes
for PID in $PIDS; do
    echo "💀 Killing process $PID..."
    if kill -$SIGNAL $PID 2>/dev/null; then
        echo "✅ Successfully sent SIG$SIGNAL to process $PID"
    else
        echo "❌ Failed to kill process $PID (might already be dead)"
    fi
done

# Wait a moment and check if processes are gone
sleep 2

REMAINING_PIDS=$(lsof -ti tcp:$PORT 2>/dev/null || true)
if [ -z "$REMAINING_PIDS" ]; then
    echo "✅ All processes on port $PORT have been terminated"
else
    echo "⚠️  Some processes are still running on port $PORT:"
    lsof -i tcp:$PORT
    if [ "$FORCE" != "--force" ]; then
        echo "💡 Try running with --force flag to use SIGKILL"
    fi
fi