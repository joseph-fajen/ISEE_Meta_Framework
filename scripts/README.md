# ISEE Meta Framework - Development Scripts

This directory contains robust development scripts for managing your Flask application on localhost:5001, with proper process lifecycle management and port cleanup utilities.

## 📁 Scripts Overview

| Script | Purpose | Usage |
|--------|---------|-------|
| `dev-server.sh` | 🚀 **Main development server management** | `./dev-server.sh {start\|stop\|restart\|status\|logs}` |
| `kill-port.sh` | 💀 Kill processes on specific port | `./kill-port.sh <port> [--force]` |
| `check-ports.sh` | 🔍 Check status of development ports | `./check-ports.sh [port1] [port2] ...` |
| `kill-dev-ports.sh` | 🧹 Clean all common dev ports | `./kill-dev-ports.sh [--force]` |
| `dev-aliases.sh` | ⚡ Shell aliases and functions | `source dev-aliases.sh` |
| `install-aliases.sh` | 🔧 Install aliases in shell config | `./install-aliases.sh [--shell bash\|zsh]` |

## 🚀 Quick Start - Transform Your Daily Workflow

**🔄 STOP using `python app.py` - START using these scripts for better development experience!**

### Why Switch from `python app.py`?

**❌ Problems with `python app.py`:**
- Process gets lost when terminal closes
- No graceful shutdown (Ctrl+C sometimes fails)
- Port conflicts from lingering processes  
- No persistent logging
- Manual cleanup required

**✅ Benefits of script-based workflow:**
- Background operation (independent of terminal)
- PID tracking and graceful shutdown
- Automatic port conflict resolution
- Persistent logging to `dev-server.log`
- Status monitoring and process management

### 1. Install Aliases (HIGHLY RECOMMENDED - Do This First!)

```bash
# One-time setup (takes 30 seconds)
./scripts/install-aliases.sh
source ~/.zshrc  # or ~/.bashrc, or just restart terminal

# Test installation
isee-help       # Should show all available commands
```

### 2. Your New Daily Workflow

**🎯 Simple Daily Commands (after alias installation):**
```bash
# Start your development session
isee-start      # Replaces: python app.py

# Open browser (optional - add to your workflow)
open http://localhost:5001

# Check server status anytime
isee-status     # Shows running/stopped + recent logs

# View logs for debugging (GAME CHANGER!)
isee-logs       # Real-time log following

# Stop cleanly when done
isee-stop       # Always clean shutdown
```

**🔧 Alternative: Direct Script Usage (if you prefer not using aliases):**
```bash
./scripts/dev-server.sh start    # Replaces: python app.py
./scripts/dev-server.sh status   # Check status
./scripts/dev-server.sh logs     # View logs  
./scripts/dev-server.sh stop     # Clean stop
```

### 3. Port Conflict Resolution (When Things Go Wrong)

```bash
# Diagnose port issues
isee-ports      # or: ./scripts/check-ports.sh

# Fix specific port conflicts
isee-kill-port 5001    # or: ./scripts/kill-port.sh 5001

# Nuclear option - clean everything
isee-kill-dev-ports    # or: ./scripts/kill-dev-ports.sh
```

## 🔧 Detailed Usage

### Development Server Management (`dev-server.sh`)

The main script provides robust Flask application lifecycle management:

**Start Server:**
```bash
./scripts/dev-server.sh start
```
- ✅ Checks for existing processes and cleans up port 5001
- ✅ Starts server in background with PID tracking
- ✅ Validates successful startup
- ✅ Shows server URL and log file location

**Check Status:**
```bash
./scripts/dev-server.sh status
```
- ✅ Shows running/stopped status
- ✅ Displays process details (PID, port, URL)
- ✅ Shows recent log entries
- ✅ Detects port conflicts with other processes

**View Logs:**
```bash
./scripts/dev-server.sh logs
```
- ✅ Real-time log following (like `tail -f`)
- ✅ Press Ctrl+C to exit

**Stop Server:**
```bash
./scripts/dev-server.sh stop
```
- ✅ Graceful shutdown attempt (SIGTERM)
- ✅ Force kill if graceful fails (SIGKILL)
- ✅ Cleanup of PID files and port conflicts
- ✅ 10-second timeout for graceful shutdown

### Port Management Scripts

**Check Ports (`check-ports.sh`):**
```bash
# Check default development ports (3000, 5000, 5001, 8000, 8080, 8888, 9000)
./scripts/check-ports.sh

# Check specific ports
./scripts/check-ports.sh 5001 3000 8080
```

**Kill Specific Port (`kill-port.sh`):**
```bash
# Graceful termination
./scripts/kill-port.sh 5001

# Force kill (immediate)
./scripts/kill-port.sh 5001 --force
```

**Clean All Dev Ports (`kill-dev-ports.sh`):**
```bash
# Clean all common development ports
./scripts/kill-dev-ports.sh

# Force clean all ports
./scripts/kill-dev-ports.sh --force
```

### Shell Aliases (`dev-aliases.sh`)

Provides 25+ convenient commands after installation:

**Navigation:**
- `isee-cd` - Navigate to project directory
- `isee-scripts` - Navigate to scripts directory

**Server Management:**
- `isee-start` - Start development server
- `isee-stop` - Stop development server
- `isee-restart` - Restart development server
- `isee-status` - Show server status
- `isee-logs` - Follow server logs

**Port Management:**
- `isee-ports` - Check common development ports
- `isee-kill-port <port>` - Kill processes on specific port
- `isee-kill-dev-ports` - Kill processes on all dev ports

**Development Workflow:**
- `isee-setup` - Full development environment setup
- `isee-clean` - Clean up all development processes
- `isee-reset` - Reset development environment
- `isee-dev` - Quick development status check

**Testing & Configuration:**
- `isee-test` - Run quick parameter validation tests
- `isee-config` - Check configuration status
- `isee-deps` - Install/update dependencies

## 🎯 Daily Development Workflows - Your Practical Scenarios

### 💡 Workflow Comparison: Old vs New

**❌ Your Old `python app.py` Workflow:**
```bash
# Start (blocks terminal, no background operation)
cd /Users/josephfajen/git/ISEE_Meta_Framework
python app.py
# Terminal is now tied up...

# Stop (hope Ctrl+C works, often leaves lingering processes)
^C

# Check for problems (manual detective work)
lsof -i :5001
kill -9 <pid>  # if needed
```

**✅ Your New Script-Based Workflow:**
```bash
# Start (from anywhere, runs in background)
isee-start
# ✅ Server started successfully!
# ✅ URL: http://localhost:5001
# ✅ Logs: dev-server.log
# Terminal free for other tasks!

# Stop (always clean, automatic cleanup)
isee-stop
# ✅ Server stopped gracefully
```

### Scenario 1: Typical Daily Development Session

**🎯 Morning Startup (Recommended Routine):**
```bash
# Quick environment check and startup
isee-status                       # Is anything already running?
isee-start                        # Start fresh
open http://localhost:5001        # Open browser
```

**🔄 During Development:**
```bash
# Check server status anytime
isee-status                       # Quick health check

# Debug issues with persistent logs
isee-logs                         # View real-time logs (Press Ctrl+C to exit)
tail -f dev-server.log           # Alternative log viewing

# Restart server after code changes (if needed)
isee-restart                     # Clean restart
```

**🌙 End of Day:**
```bash
isee-stop                        # Clean shutdown
```

### Scenario 2: "Server Won't Start" - Port Conflicts

**🚨 Problem:** You get "port already in use" error

**🎯 Solution:**
```bash
# Diagnose what's using your ports
isee-ports                       # Quick overview
lsof -i :5001                    # Detailed view of port 5001

# Fix the specific conflict
isee-kill-port 5001              # Kill just port 5001
# OR
isee-kill-dev-ports              # Nuclear option - clean all dev ports

# Start fresh
isee-start
```

### Scenario 3: "Something's Wrong" - Debugging Session

**🚨 Problem:** Server seems unresponsive or behaving strangely

**🎯 Debugging Workflow:**
```bash
# Check if server is actually running
isee-status                      # Shows PID, port, recent logs

# Look at recent activity
isee-logs                        # Real-time log following

# Check for port conflicts
isee-ports                       # See what else might interfere

# Clean restart if needed
isee-restart                     # Stop + clean + start
```

### Scenario 4: "Fresh Start" - Clean Environment Reset

**🎯 Complete Reset (when things are really messed up):**
```bash
# Nuclear option - clean everything
isee-stop                        # Stop server
isee-kill-dev-ports              # Clean all development ports
isee-start                       # Start fresh

# OR - one command reset
isee-reset                       # Does all of the above
```

### Scenario 5: "Working on Multiple Projects"

**🎯 Location Independence (with aliases):**
```bash
# Server management works from anywhere
cd ~/Documents/some-other-project
isee-status                      # Check ISEE server status
isee-logs                        # View ISEE logs

# Navigate back to project when needed
isee-cd                          # Jump to ISEE project directory
```

### Scenario 6: "Sharing with Team/Documentation"

**🎯 When explaining to others or writing docs:**
```bash
# Use full script paths for clarity
./scripts/dev-server.sh start    # Clear, explicit
./scripts/check-ports.sh         # Easy to understand

# Aliases are for your personal workflow
isee-start                       # Personal convenience
```

## 🛠 Advanced Features

### Server Management Features

- **PID File Tracking:** Server process ID stored in `.dev-server.pid`
- **Log File Management:** All output captured in `dev-server.log`
- **Graceful Shutdown:** 10-second timeout before force kill
- **Port Conflict Detection:** Automatically detects and resolves port conflicts
- **Dependency Validation:** Checks for `app.py` and `requirements.txt`

### Port Management Features

- **Smart Process Detection:** Uses `lsof` for accurate port usage detection
- **Graceful vs Force Kill:** Choose between SIGTERM and SIGKILL
- **Batch Operations:** Clean multiple ports simultaneously
- **Safety Checks:** Validates port numbers and process existence

### Shell Integration Features

- **Auto-completion:** Tab completion for common port numbers
- **Color-coded Output:** Green/red/yellow status indicators
- **Directory Awareness:** Warns if not in project directory
- **Cross-shell Compatibility:** Works with bash and zsh

## 🔍 Troubleshooting

### Common Issues

**Issue: "Permission denied" when running scripts**
```bash
# Fix: Make scripts executable
chmod +x scripts/*.sh
```

**Issue: "Port still in use after stopping server"**
```bash
# Solution: Force cleanup
./scripts/kill-port.sh 5001 --force
```

**Issue: "Server starts but can't access http://localhost:5001"**
```bash
# Check server logs
./scripts/dev-server.sh logs

# Check if server is actually running on the port
./scripts/check-ports.sh
```

**Issue: "Multiple Python processes running"**
```bash
# See all Python processes
ps aux | grep python

# Clean up development ports
./scripts/kill-dev-ports.sh --force
```

### Log Files

- **Server logs:** `dev-server.log` (in project root)
- **PID file:** `.dev-server.pid` (in project root)
- **Script output:** All scripts provide colored, timestamped output

### Validation Commands

```bash
# Test all scripts are working
./scripts/check-ports.sh
./scripts/dev-server.sh status
ls -la scripts/*.sh              # Verify all are executable

# Test aliases (after installation)
isee-help                        # Should show all available commands
```

## 🔑 Key Questions Answered

### "What's the difference between `isee-start` and `./scripts/dev-server.sh start`?"

**Answer: They do exactly the same thing!**

| Aspect | `./scripts/dev-server.sh start` | `isee-start` |
|--------|---------------------------|------------|
| **Functionality** | ✅ Identical | ✅ Identical |
| **Directory requirement** | Must be in project root | Works from anywhere |
| **Typing** | 32 characters | 10 characters |
| **Best for** | Documentation, sharing | Daily personal workflow |

**Recommendation:** Install aliases and use `isee-start` for daily work - you'll love the convenience!

### "Should I stop using `python app.py`?"

**YES! Here's why:**

**❌ `python app.py` problems:**
- Blocks your terminal
- No persistent logging
- Difficult to manage process
- Port conflicts when things go wrong
- No graceful shutdown

**✅ `isee-start` advantages:**
- Runs in background (terminal stays free)
- Persistent logging to `dev-server.log`
- Proper process management with PID tracking
- Automatic port conflict resolution
- Graceful shutdown with fallback to force kill

### "Where are my logs and how do I use them?"

**Log file location:** `dev-server.log` in your project root

**Viewing logs:**
```bash
# Real-time log following (best for debugging)
isee-logs                        # Press Ctrl+C to exit

# Alternative log viewing methods
tail -f dev-server.log          # Direct file access
tail -n 50 dev-server.log       # Last 50 lines
less dev-server.log             # Browse entire log file
```

**Why logs are a game-changer:**
- ✅ **Persistent:** Logs survive terminal closures
- ✅ **Timestamps:** See exactly when things happened
- ✅ **Complete:** Captures all Flask output + script messages
- ✅ **Debugging:** Essential for troubleshooting issues

## 🎉 Summary - Your Development Transformation

**🔄 TRANSFORMATION CHECKLIST:**

1. **✅ Install aliases** (one-time, 30 seconds):
   ```bash
   ./scripts/install-aliases.sh && source ~/.zshrc
   ```

2. **✅ Replace `python app.py` with `isee-start`** in your daily routine

3. **✅ Use `isee-logs`** when debugging (replaces trying to remember console output)

4. **✅ Use `isee-status`** to check server health anytime

5. **✅ Use `isee-stop`** for clean shutdowns (no more lingering processes)

**🎯 DAILY ROUTINE BECOMES:**
```bash
# Morning
isee-start && open http://localhost:5001

# During development
isee-status      # Quick health check
isee-logs        # Debug when needed
isee-restart     # Clean restart if needed

# End of day
isee-stop        # Clean shutdown
```

**🎊 BENEFITS YOU'LL EXPERIENCE:**
- ✅ **No more "port already in use" headaches**
- ✅ **Persistent logs for better debugging**
- ✅ **Terminal freedom** (background server operation)
- ✅ **Consistent, reliable server management**
- ✅ **Professional-grade development workflow**
- ✅ **Works from any directory** (with aliases)
- ✅ **Automatic cleanup** (no manual process hunting)

---

*This README is your daily companion for ISEE development. Bookmark it, refer to it, and watch your development experience transform from frustrating to fantastic!*