# PM Performance Manager

A Windows performance tuning and system management tool with a modern dark UI. Built with Python and CustomTkinter.

## Features

- **Dashboard** — Live CPU, RAM, GPU, and disk monitoring with top processes
- **Gaming Mode** — High-performance power plan, Windows Update disable, game detection
- **Performance Mode** — Restore point, temp/shader/prefetch cleanup, SSD TRIM
- **Health Check** — DISM, SFC, SMART status, TRIM checks
- **Network Repair** — DNS flush, Winsock reset, IP stack reset, traffic stats
- **Drives & Storage** — Per-drive usage and SMART status
- **Startup Manager** — Registry and startup folder management
- **System Info** — Detailed OS/CPU/RAM/GPU/motherboard/network info
- **Privacy Blocker** — Block telemetry services, hosts, registry entries
- **Services Manager** — Enable/disable Windows services with safety badges
- **Bloatware Uninstaller** — Batch uninstall 40+ known bloatware packages
- **Hosts File Editor** — Add/remove/toggle hosts entries
- **RAM Optimizer** — Free memory and kill processes
- **Large File Finder** — Recursive disk scan by size threshold
- **Battery Report** — WMI battery info + powercfg report
- **Windows Features** — Toggle 16 optional features via DISM
- **Visual Effects** — Toggle animations, transparency, startup sound
- **Speed Test** — Download speed test + latency to multiple servers
- **Plugin System** — Extensible via JSON manifest plugins
- **Scheduled Maintenance** — Automatic cleanup, DISM, SFC on schedule
- **Theme Support** — Dark/Light/System appearance + color themes

## Download

Download the latest `PMPerformanceManager.exe` from [Releases](https://github.com/pmdm/PM-Performance-Manager/releases).

**Requirements:** Windows 10 or 11. No Python or dependencies needed — it's a standalone executable.

## Usage

Run `PMPerformanceManager.exe` — it will auto-elevate to administrator (most features require admin privileges).

Configuration is saved to `%LOCALAPPDATA%\PMPerformanceManager\config.json`.

## Development

```bash
# Clone
git clone https://github.com/pmdm/PM-Performance-Manager.git
cd PM-Performance-Manager

# Install deps
pip install -r requirements.txt

# Run
python main.py

# Build
pyinstaller --onefile --windowed --name PMPerformanceManager --add-data "app;app" --uac-admin main.py
```

Requires Python 3.12+ and Windows SDK for the `--uac-admin` PyInstaller flag.
