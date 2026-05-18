🕶️ C2 FRAMEWORK
 ██████╗██████╗     ███████╗██████╗  █████╗ ███╗   ███╗███████╗██╗    ██╗ ██████╗ ██████╗ ██╗  ██╗
██╔════╝╚════██╗    ██╔════╝██╔══██╗██╔══██╗████╗ ████║██╔════╝██║    ██║██╔═══██╗██╔══██╗██║ ██╔╝
██║      █████╔╝    █████╗  ██████╔╝███████║██╔████╔██║█████╗  ██║ █╗ ██║██║   ██║██████╔╝█████╔╝
██║     ██╔═══╝     ██╔══╝  ██╔══██╗██╔══██║██║╚██╔╝██║██╔══╝  ██║███╗██║██║   ██║██╔══██╗██╔═██╗
╚██████╗███████╗    ██║     ██║  ██║██║  ██║██║ ╚═╝ ██║███████╗╚███╔███╔╝╚██████╔╝██║  ██║██║  ██╗
 ╚═════╝╚══════╝    ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝ ╚══╝╚══╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝
<div align="center">
🛡️ C2 Framework
Enterprise-Grade Command & Control Infrastructure

Educational Red Teaming • Detection Engineering • Malware Analysis • Adversary Simulation

<br>










</div>
⚠️ WARNING — EDUCATIONAL PURPOSE ONLY

This framework is intended exclusively for:

Cybersecurity education
Malware analysis training
Authorized penetration testing
Red team simulations
Detection engineering
Controlled lab environments

Unauthorized use against systems you do not own or explicitly have permission to test is illegal and unethical.

🎯 Overview

This C2 Framework is an educational command-and-control simulation platform designed to demonstrate how modern post-exploitation infrastructure works inside controlled cybersecurity labs.

The framework helps:

Red Teamers
Blue Teamers
SOC Analysts
Malware Analysts
Students
Cybersecurity Researchers

understand:

Beaconing mechanisms
Encrypted communications
Persistence techniques
Detection engineering
Adversary tradecraft
Incident response workflows
✨ Features
🧠 Core Capabilities
Feature	Description	Status
Multi-Platform Agents	Windows / Linux / macOS	✅
HTTP/HTTPS C2 Channels	REST-based encrypted communication	✅
Real-Time Dashboard	Operator web console	✅
Multi-Agent Management	Simultaneous session handling	✅
Task Queue System	Async command execution	✅
File Transfer	Upload / Download simulation	✅
Persistence Modules	OS-specific persistence examples	✅
Screenshot Module	Educational screen capture	✅
AES Encryption	Secure communications	✅
Logging & Monitoring	Event tracking system	✅
🔧 Technical Specifications
Component	Technology
Backend	Flask REST API
Encryption	AES-256-GCM
Dashboard	HTML5 + JavaScript
Database	SQLite / MySQL
Communication	JSON over HTTP/HTTPS
Payload Delivery	Python HTTP Server
Beaconing	Configurable Jitter
Deployment	Apache2 / Nginx
🏗️ Architecture
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
│  │                C2 SERVER (Flask)                     │  │
│  │           Port 443 / 5000 (HTTPS/HTTP)              │  │
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
🚀 Quick Start Guide
Step 1 — Clone Repository
git clone https://github.com/parrysecurity/C2-Framework.git

cd C2-Framework
Step 2 — Install Dependencies
pip3 install flask flask-cors requests pycryptodome
Step 3 — Start C2 Server
python3 c2_server_http.py
Step 4 — Start Payload Hosting Server
cd payloads

python3 -m http.server 8000
Step 5 — Access Dashboard
http://127.0.0.1:5000
🛡️ Detection & Defense

This project also teaches defensive security concepts.

Network Indicators
Indicators:
  - Repeated HTTP POST requests
  - Beacon intervals with jitter
  - Suspicious User-Agent strings
  - JSON payloads to /api/beacon
Host Indicators
Windows
Unusual Python processes
Registry Run keys
Scheduled Tasks
Linux
Suspicious cron jobs
Unknown outbound connections
Persistence scripts
📁 Project Structure
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
⚖️ Legal & Ethics
✅ Permitted Usage
Educational labs
Red team exercises
Malware analysis
Academic research
Detection engineering
❌ Prohibited Usage
Unauthorized access
Production deployment
Data theft
Malicious activity
Illegal operations
📄 License
EDUCATIONAL USE ONLY LICENSE

This project is provided strictly for:
- Cybersecurity education
- Defensive research
- Authorized testing
- Controlled environments

Unauthorized usage is prohibited.
<div align="center">
🛡️ Learn Offense to Build Better Defense
Educational Research Project by ParrySecurity

⭐ Star the repository if you found it useful.

</div>
