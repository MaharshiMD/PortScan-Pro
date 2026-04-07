# PortScan Pro 🛡️

A highly professional, rapid, multithreaded Python network port scanner built with socket programming. It quickly identifies open ports, performs initial host discovery, determines associated services, and grabs service banners for deep insights.

## Features

- **Fast Multithreading**: Configurable thread pooling allows you to run hundreds of simultaneous connections, drastically reducing scan time.
- **Host Discovery (Ping Sweep)**: Automatically evaluates if a target IP/Domain is online utilizing ICMP pings before attempting to map ports, saving valuable time.
- **Service Identification**: Matches open network ports to standard protocol services (e.g., HTTP on 80, MySQL on 3306) and intelligently questions the underlying OS when unsure.
- **Banner Grabbing**: Grabs initial packets of data sent by services to accurately version-check underlying software and protocols.
- **Advanced CLI Arguments**: Use professional flags natively in the command-line to integrate into bash/python automation scripts.
- **Rich Reporting**: Generate powerful visual and programmatic exports in `.JSON`, `.CSV`, and elegant `.HTML` layouts.
- **Modern Graphical UI**: Full desktop Tkinter interface complete with live progress bars, threading adjustments, export selection fields, and a scrollable log.

## Requirements
No external third-party `pip` installations are required. Everything is managed natively within the standard Python framework.
```text
- socket, threading, queue, datetime, json, csv, subprocess, platform, argparse, sys, tkinter
```
*Requires **Python 3.x***.

## 1. Command-Line Interface (CLI)
Open your terminal and run it natively:

**Basic Example:**
```bash
python scanner.py scanme.nmap.org -p 80-443
```
**Full Professional Example:**
```bash
python scanner.py 192.168.1.1 -p 1-1000 --threads 200 --timeout 0.3 --export html
```

### CLI Arguments:
| Argument | Description | Example |
| :--- | :--- | :--- |
| `target` | **(Required)** Target IP address or domain name. | `python scanner.py google.com` |
| `-c`, `--common` | Scans the internal dictionary of 12 common ports. | `-c` |
| `-p`, `--ports` | Specify a custom range of ports to hunt through. | `-p 1-5000` |
| `-t`, `--threads` | Define amount of concurrent threads. *(Default: 100)* | `-t 250` |
| `-T`, `--timeout` | Packet waiting timeout in seconds. *(Default: 0.5)* | `-T 0.2` |
| `--export` | Generate an output log (`json`, `csv`, `html`, `all`). | `--export all` |
| `--skip-ping` | Bypass the initial ICMP Host Up/Down check mechanism. | `--skip-ping` |

## 2. Graphical User Interface (GUI)
To use the visual application, easily boot it via python:
```bash
python gui.py
```
This launches a standalone window where you can:
- Key in the **IP Target**.
- Enter exact **start and end** ports.
- Tweak **Timeout Limits** based on internet connection speeds.
- Slide through the background-managed **Live Progress Bar**.
- Expand the Export Combobox to instantly generate `.html` or `.csv` spreadsheets directly to the local folder.

## Project Structure
```text
PortScan Pro/
├── scanner.py        # Core multithreaded scanning logic and CLI interface
├── gui.py            # Tkinter desktop application interface
├── requirements.txt  # Description of required built-in modules
└── README.md         # Readme instructions
```

> **Legal Disclaimer:**
> **For Educational Purposes Only.** This tool is intended strictly for network administration, academic research, and personal systems auditing. You should only run diagnostics or port scans against physical networks and remote hardware you own or possess explicitly written permission to test. Unauthorized port scanning can result in severe ISP restrictions, IP blacklisting, or potential legal consequences depending on jurisdiction.
