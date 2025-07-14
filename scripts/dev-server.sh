#!/bin/bash

# Development server management script for ISEE Meta Framework
# Usage: ./dev-server.sh {start|stop|restart|status|logs}

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
PID_FILE="$PROJECT_DIR/.dev-server.pid"
LOG_FILE="$PROJECT_DIR/dev-server.log"
PORT=5001

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

check_dependencies() {
    if [ ! -f "$PROJECT_DIR/app.py" ]; then
        error "app.py not found in project directory"
        exit 1
    fi
    
    if [ ! -f "$PROJECT_DIR/requirements.txt" ]; then
        warning "requirements.txt not found - dependencies might not be installed"
    fi
}

get_server_pid() {
    if [ -f "$PID_FILE" ]; then
        cat "$PID_FILE"
    else
        echo ""
    fi
}

is_server_running() {
    local pid=$(get_server_pid)
    if [ -n "$pid" ] && ps -p "$pid" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

cleanup_port() {
    log "Cleaning up port $PORT..."
    "$SCRIPT_DIR/kill-port.sh" "$PORT" || true
}

start_server() {
    check_dependencies
    
    if is_server_running; then
        local pid=$(get_server_pid)
        warning "Server is already running (PID: $pid)"
        log "Server accessible at: http://localhost:$PORT"
        return 0
    fi
    
    # Clean up any lingering processes on the port
    cleanup_port
    
    log "Starting development server..."
    log "Project directory: $PROJECT_DIR"
    log "Log file: $LOG_FILE"
    
    # Start server in background
    cd "$PROJECT_DIR"
    nohup python app.py > "$LOG_FILE" 2>&1 &
    local server_pid=$!
    
    # Save PID
    echo "$server_pid" > "$PID_FILE"
    
    # Wait a moment and check if server started successfully
    sleep 3
    
    if is_server_running; then
        success "Development server started successfully!"
        log "PID: $server_pid"
        log "Port: $PORT"
        log "URL: http://localhost:$PORT/isee-ui"
        log "Logs: tail -f $LOG_FILE"
    else
        error "Failed to start development server"
        if [ -f "$LOG_FILE" ]; then
            error "Check logs for details:"
            tail -n 10 "$LOG_FILE"
        fi
        exit 1
    fi
}

stop_server() {
    if ! is_server_running; then
        warning "Server is not running"
        # Clean up stale PID file
        [ -f "$PID_FILE" ] && rm "$PID_FILE"
        cleanup_port
        return 0
    fi
    
    local pid=$(get_server_pid)
    log "Stopping development server (PID: $pid)..."
    
    # Try graceful shutdown first
    if kill -TERM "$pid" 2>/dev/null; then
        log "Sent SIGTERM, waiting for graceful shutdown..."
        
        # Wait up to 10 seconds for graceful shutdown
        for i in {1..10}; do
            if ! ps -p "$pid" > /dev/null 2>&1; then
                success "Server stopped gracefully"
                rm -f "$PID_FILE"
                return 0
            fi
            sleep 1
        done
        
        # Force kill if graceful shutdown failed
        warning "Graceful shutdown failed, forcing termination..."
        kill -KILL "$pid" 2>/dev/null || true
    fi
    
    # Clean up
    rm -f "$PID_FILE"
    cleanup_port
    success "Development server stopped"
}

restart_server() {
    log "Restarting development server..."
    stop_server
    sleep 2
    start_server
}

show_status() {
    echo "================================"
    echo "ISEE Meta Framework - Dev Server Status"
    echo "================================"
    
    if is_server_running; then
        local pid=$(get_server_pid)
        success "Server is RUNNING"
        echo "PID: $pid"
        echo "Port: $PORT"
        echo "URL: http://localhost:$PORT/isee-ui"
        echo "Log file: $LOG_FILE"
        
        echo ""
        echo "Process details:"
        ps -fp "$pid" || true
    else
        warning "Server is NOT running"
        
        # Check if port is occupied by other processes
        local port_processes=$(lsof -ti tcp:$PORT 2>/dev/null || true)
        if [ -n "$port_processes" ]; then
            warning "Port $PORT is occupied by other processes:"
            lsof -i tcp:$PORT || true
        fi
    fi
    
    echo ""
    echo "Recent log entries:"
    if [ -f "$LOG_FILE" ]; then
        tail -n 5 "$LOG_FILE"
    else
        echo "No log file found"
    fi
    echo "================================"
}

show_logs() {
    if [ -f "$LOG_FILE" ]; then
        log "Showing development server logs (Press Ctrl+C to exit):"
        tail -f "$LOG_FILE"
    else
        warning "Log file not found: $LOG_FILE"
    fi
}

# Main script logic
case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start    - Start the development server"
        echo "  stop     - Stop the development server"
        echo "  restart  - Restart the development server"
        echo "  status   - Show server status and recent logs"
        echo "  logs     - Follow server logs in real-time"
        echo ""
        echo "Server URL: http://localhost:$PORT/isee-ui"
        echo "Project: ISEE Meta Framework"
        exit 1
        ;;
esac